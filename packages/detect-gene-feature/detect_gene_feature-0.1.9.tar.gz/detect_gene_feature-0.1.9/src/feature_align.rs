#![allow(unused)]
use crate::fasta::{self, FastaSeq};
use crate::seq_trees::{AlignResult, SeqTrees};
use crate::utils::print_align_map_ref;
use calamine::{open_workbook, DataType, Error, Reader, Xlsx};
use crossbeam_channel::{bounded, Receiver, Sender};
use csv;
use debug_print::{debug_eprintln, debug_println};
use flate2::read::MultiGzDecoder;
use fnv::FnvHashMap;
use rayon::{iter, prelude::*, vec};
use regex::Regex;
use serde::Serialize;
use std::cmp;
use std::fs::File;
use std::fs::OpenOptions;
use std::io::prelude::*;
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::thread;

// pub type FeatureInfo = (String, String, bool, String, String, bool, u32);
// type FeatureRegion = (usize, usize, isize, usize, f32, u32, usize, usize, usize);

#[derive(Debug, Clone)]
struct FeatureRegion {
    ref_start: usize,
    ref_end: usize,
    score: isize,
    mapped_base: usize,
    similarity: f32,
    level: u32,
    group_id: usize,
    feature_id: usize,
    align_id: usize,
}

#[derive(Debug, Serialize)]
pub struct FeatureInfo {
    fid: String,
    name: String,
    mode: bool,
    dna: String,
    aa: String,
    overlap: bool,
    level: u32,
}

impl FeatureInfo {
    pub fn to_tuple(self) -> (String, String, bool, String, String, bool, u32) {
        (
            self.fid,
            self.name,
            self.mode,
            self.dna,
            self.aa,
            self.overlap,
            self.level,
        )
    }
    pub fn from_tuple(fi: (String, String, bool, String, String, bool, u32)) -> Self {
        FeatureInfo {
            fid: fi.0,
            name: fi.1,
            mode: fi.2,
            dna: fi.3,
            aa: fi.4,
            overlap: fi.5,
            level: fi.6,
        }
    }
}

pub type AlignTuple = (
    String,
    usize,
    usize,
    bool,
    f32,
    usize,
    usize,
    isize,
    bool,
    bool,
    String,
    String,
);

pub fn load_features(feature_path: &Path) -> Result<Vec<FeatureInfo>, Error> {
    let mut excel: Xlsx<_> = open_workbook(feature_path).unwrap();
    let mut feature_list = vec![];
    let mut fid_idx: usize = 0;
    let mut name_idx: usize = 0;
    let mut mode_idx: usize = 0;
    let mut dna_idx: usize = 0;
    let mut aa_idx: usize = 0;
    let mut overlap_idx: usize = 0;
    let itr_re = Regex::new(r"ITR[^0-9]*([0-9]+)").unwrap();
    if let Some(Ok(r)) = excel.worksheet_range("Sheet1") {
        for (num, row) in r.rows().enumerate() {
            if num == 0 {
                for (idx, cell) in row.iter().enumerate() {
                    match cell {
                        DataType::String(x) => {
                            if x == "index" {
                                fid_idx = idx;
                            } else if x == "name" {
                                name_idx = idx;
                            } else if x == "detectionMode" {
                                mode_idx = idx;
                            } else if x == "seq" {
                                dna_idx = idx;
                            } else if x == "aa_seq" {
                                aa_idx = idx;
                            } else if x == "gs_allow_overlap" {
                                overlap_idx = idx;
                            } else {
                            }
                        }
                        _ => {}
                    }
                }
                if fid_idx == 0
                    && name_idx == 0
                    && mode_idx == 0
                    && dna_idx == 0
                    && aa_idx == 0
                    && overlap_idx == 0
                {
                    panic!("Can't get feature header.")
                }
            } else {
                let fid = row[fid_idx].get_string().unwrap().to_owned();
                let name = row[name_idx].get_string().unwrap().to_owned();
                let mode = match row[mode_idx].get_string() {
                    Some("exactProteinMatch") => true,
                    _ => false,
                };
                let dna = row[dna_idx]
                    .get_string()
                    .unwrap()
                    .to_owned()
                    .replace(",", "")
                    .replace(" ", "");
                let aa = match row[aa_idx].get_string() {
                    Some(x) => x.to_owned().replace(",", "").replace(" ", ""),
                    _ => "".to_owned(),
                };
                let overlap = match row[overlap_idx].get_float(){
                    Some(x) =>{let x_u32= x as u32;
                        match x_u32{
                        0 => false,
                        1 => true,
                        _=> panic!(
                            "Feature overlap information Error {overlap_idx} ({overlap:?})\n Row: {row:#?} ",
                            overlap = row[overlap_idx]
                        ),
                    }}
                    None => panic!(
                        "Feature overlap information Error {overlap_idx} ({overlap:?})\n Row: {row:#?} ",
                        overlap = row[overlap_idx]
                    ),
                };
                let level = match name.to_uppercase() == "ITR" {
                    true => {
                        let caps = itr_re.captures(&fid).unwrap();
                        caps.get(1).unwrap().as_str().parse::<u32>().unwrap()
                    }
                    false => 0,
                };
                let info = FeatureInfo {
                    fid,
                    name,
                    mode,
                    dna,
                    aa,
                    overlap,
                    level,
                };
                // println!("{info:?}");
                feature_list.push(info);
            }
        }
    }
    Ok(feature_list)
}

pub fn align_single_feature<'a, 'b>(
    feature_info: &'a FeatureInfo,
    seq_tree: &'b SeqTrees,
    match_score: isize,
    mismatch_score: isize,
    gap_open: isize,
    gap_extend: isize,
    min_similarity: f32,
) -> (&'a FeatureInfo, Vec<AlignResult>) {
    let align_result = if feature_info.mode == true {
        seq_tree.align_aa(
            &feature_info.aa,
            &feature_info.dna,
            cmp::max(3, feature_info.aa.len() / 2 as usize),
            feature_info.aa.len(),
            match_score,
            mismatch_score,
            gap_open,
            gap_extend,
            min_similarity,
        )
    } else {
        seq_tree.align_dna(
            &feature_info.dna,
            cmp::max(5, feature_info.dna.len() / 2 as usize),
            feature_info.dna.len(),
            match_score,
            mismatch_score,
            gap_open,
            gap_extend,
            min_similarity,
        )
    };
    (feature_info, align_result)
}

fn overlap_remove(mut features: Vec<FeatureRegion>) -> (Vec<FeatureRegion>, Vec<FeatureRegion>) {
    if features.len() == 0 {
        return (vec![], vec![]);
    }
    features.sort_by_key(|x| (x.ref_start, x.ref_end, x.score, x.feature_id));
    let mut selected = vec![];
    let mut dropped = vec![];
    let mut current_pointer = 0;
    for pointer in 1..features.len() {
        if features[current_pointer].ref_end > features[pointer].ref_start {
            //overlap current end bigger than next start
            // replace mapped_base with score
            if features[current_pointer].score < features[pointer].score {
                //current feature match count less than next feature
                dropped.push(current_pointer);
                current_pointer = pointer;
            } else if features[current_pointer].score == features[pointer].score {
                //current feature match count equal next feature
                if features[current_pointer].similarity < features[pointer].similarity {
                    //current feature similarity less than next feature
                    dropped.push(current_pointer);
                    current_pointer = pointer;
                } else if features[current_pointer].similarity == features[pointer].similarity {
                    //current feature similarity equal next feature
                    if features[current_pointer].group_id == features[pointer].group_id
                        && features[current_pointer].level < features[pointer].level
                    {
                        // current level less than next feature
                        dropped.push(current_pointer);
                        current_pointer = pointer;
                    } else {
                        dropped.push(pointer);
                    }
                } else {
                    //current feature similarity bigger than next feature
                    dropped.push(pointer);
                }
            } else {
                //current feature match count bigger than next feature
                dropped.push(pointer);
            }
        } else {
            //not overlap select currect region and pointer is new current region
            selected.push(current_pointer);
            current_pointer = pointer;
        }
    }
    // if selected.len() == 0 || current_pointer != selected[selected.len() - 1] {
    //     selected.push(current_pointer);
    // }
    selected.push(current_pointer);
    assert_eq!(selected.len() + dropped.len(), features.len());
    assert!(
        selected.len() != 0,
        "{selected:?}\n{dropped:?}\n{features:?}"
    );
    let mut selected_features = vec![];
    let mut dropped_features = vec![];
    for (num, feature) in features.into_iter().enumerate() {
        if selected.contains(&num) {
            selected_features.push(feature);
        } else {
            assert!(dropped.contains(&num));
            dropped_features.push(feature);
        }
    }
    (selected_features, dropped_features)
}

fn remove_overlap_features(
    seq_len: usize,
    hit_features: &Vec<(&FeatureInfo, Vec<AlignResult>)>,
) -> (Vec<FeatureRegion>, Vec<FeatureRegion>, Vec<FeatureRegion>) {
    //hit_features Vector((feature info), (feature align result))
    let mut groups = vec![];
    let mut feature_groups = FnvHashMap::default();
    for (fid, (finfo, aresults)) in hit_features.iter().enumerate() {
        if !groups.contains(&finfo.name) {
            groups.push(finfo.name.clone());
        }
        let gid = groups.iter().position(|r| r == &finfo.name).unwrap();
        let mut fg = feature_groups.entry(gid).or_insert(vec![]);
        for (aid, adata) in aresults.iter().enumerate() {
            debug_eprintln!("Position Change {} {} {}", seq_len, adata.start, adata.end);
            let (start, end) = if adata.start >= seq_len {
                (adata.start - seq_len, adata.end - seq_len)
            } else {
                (adata.start, adata.end)
            };
            let region = FeatureRegion {
                ref_start: start,
                ref_end: end,
                score: adata.align.score,
                mapped_base: adata.align.mapped_base,
                similarity: adata.align.similarity,
                level: finfo.level,
                group_id: gid,
                feature_id: fid,
                align_id: aid,
            };
            fg.push(region);
        }
    }
    let mut selected_regions = vec![];
    let mut group_selected = vec![];
    let mut group_dropped = vec![];
    for (gid, group_features) in feature_groups.into_iter() {
        if group_features.len() > 0 {
            // println!("overlap_remove counts {}", group_features.len());
            let (selected, dropped) = overlap_remove(group_features);
            let sc = selected.len();
            let dc = dropped.len();
            for region in selected {
                if hit_features[region.feature_id].0.overlap {
                    //if feature allow overlap then do not do region remove.
                    selected_regions.push(region);
                } else {
                    group_selected.push(region);
                }
            }
            group_dropped.extend(dropped);
        }
    }
    let (region_selected, region_dropped) = overlap_remove(group_selected);
    selected_regions.extend(region_selected);
    (selected_regions, group_dropped, region_dropped)
}

// pub struct FeatureInfo {
//     fid: String,
//     name: String,
//     mode: bool,
//     dna: String,
//     aa: String,
//     overlap: bool,
//     level: u32,
// }

pub fn do_align_seq(
    seq_in: String,
    liner: bool,
    query_dna: String,
    query_aa: String,
    is_aa: bool,
    match_score: isize,
    mismatch_score: isize,
    gap_open: isize,
    gap_extend: isize,
    min_similarity: f32,
) -> Vec<(usize, usize, bool, f32, usize, usize, isize, String, String)> {
    let seq_len = seq_in.len();
    let seq_tree = SeqTrees::new(seq_in, liner);
    let align_result = if is_aa == true {
        seq_tree.align_aa(
            &query_aa,
            &query_dna,
            cmp::max(3, query_aa.len() / 2 as usize),
            query_aa.len(),
            match_score,
            mismatch_score,
            gap_open,
            gap_extend,
            min_similarity,
        )
    } else {
        seq_tree.align_dna(
            &query_dna,
            cmp::max(5, query_dna.len() / 2 as usize),
            query_dna.len(),
            match_score,
            mismatch_score,
            gap_open,
            gap_extend,
            min_similarity,
        )
    };
    let mut results = vec![];
    for align in align_result {
        results.push((
            align.start,
            align.end,
            align.is_forward,
            align.align.similarity,
            align.align.mapped_base,
            align.dna_match,
            align.align.score,
            align.align.ref_str,
            align.align.alt_str.clone(),
        ))
    }
    results
}

pub fn do_feature_align(
    seq_in: String,
    liner: bool,
    features: &Vec<FeatureInfo>,
    match_score: isize,
    mismatch_score: isize,
    gap_open: isize,
    gap_extend: isize,
    min_similarity: f32,
) -> Vec<AlignTuple> {
    let seq_len = seq_in.len();
    let st = SeqTrees::new(seq_in, liner);
    // into_par_iter
    let align_result: Vec<_> = features
        .into_par_iter()
        .map(|i| {
            debug_eprintln!("{} {} start", i.fid, i.name);
            align_single_feature(
                i,
                &st,
                match_score,
                mismatch_score,
                gap_open,
                gap_extend,
                min_similarity,
            )
        })
        .filter(|x| x.1.len() > 0)
        .collect();
    debug_eprintln!("Align result {:?}", align_result);
    let (mut selected, mut group_dropped, mut region_dropped) =
        remove_overlap_features(seq_len, &align_result);
    debug_eprintln!("Align selected result {:?}", selected);
    debug_eprintln!("Align group_dropped result {:?}", group_dropped);
    debug_eprintln!("Align region_dropped result {:?}", region_dropped);
    let mut align_results = vec![];
    selected.sort_by_key(|x| x.ref_start);
    for region in selected {
        let feature = &align_result[region.feature_id];
        let align = &feature.1[region.align_id];
        // println!(
        //     "Align {}:\n{}",
        //     feature.0.fid,
        //     print_align_map_ref(align.align.score, &align.align.align_path)
        // );
        if region.ref_start < seq_len {
            align_results.push((
                feature.0.fid.clone(),
                region.ref_start,
                region.ref_end,
                align.is_forward,
                align.align.similarity,
                align.align.mapped_base,
                align.dna_match,
                align.align.score,
                feature.0.mode,
                feature.0.overlap,
                align.align.alt_str.clone(),
                "Selected".to_string(),
            ))
        } else {
            align_results.push((
                feature.0.fid.clone(),
                region.ref_start,
                region.ref_end,
                align.is_forward,
                align.align.similarity,
                align.align.mapped_base,
                align.dna_match,
                align.align.score,
                feature.0.mode,
                feature.0.overlap,
                align.align.alt_str.clone(),
                "Out_of_Bounds_Dropped".to_string(),
            ))
        }
    }
    group_dropped.sort_by_key(|x| x.ref_start);
    for region in group_dropped {
        let feature = &align_result[region.feature_id];
        let align = &feature.1[region.align_id];
        align_results.push((
            feature.0.fid.clone(),
            region.ref_start,
            region.ref_end,
            align.is_forward,
            align.align.similarity,
            align.align.mapped_base,
            align.dna_match,
            align.align.score,
            feature.0.mode,
            feature.0.overlap,
            align.align.alt_str.clone(),
            "Group_Dropped".to_string(),
        ))
    }
    region_dropped.sort_by_key(|x| x.ref_start);
    for region in region_dropped {
        let feature = &align_result[region.feature_id];
        let align = &feature.1[region.align_id];
        align_results.push((
            feature.0.fid.clone(),
            region.ref_start,
            region.ref_end,
            align.is_forward,
            align.align.similarity,
            align.align.mapped_base,
            align.dna_match,
            align.align.score,
            feature.0.mode,
            feature.0.overlap,
            align.align.alt_str.clone(),
            "Region_Dropped".to_string(),
        ))
    }
    align_results
}

pub fn write_align_result(
    align_receiver: Receiver<(usize, String, Vec<u8>)>,
    result_path: &Path,
) -> usize {
    let fileout = OpenOptions::new()
        .create(true)
        .write(true)
        .open(result_path)
        .expect(&format!("Can't open {result_path:?}"));
    let mut zipout = zip::ZipWriter::new(fileout);
    let options =
        zip::write::FileOptions::default().compression_method(zip::CompressionMethod::Stored);
    let mut seq_count = 0;
    for (num, sid, result) in align_receiver {
        seq_count += 1;
        zipout.start_file(format!("{sid}_{num}_result.csv"), options);
        zipout.write(&result);
        if seq_count % 500 == 0 {
            debug_println!("Aligned {seq_count} sequences.");
            zipout.flush().unwrap();
        }
    }
    zipout.flush().unwrap();
    debug_println!("All sequence {seq_count} aligned.");
    seq_count
}

pub fn align_consumer(
    seq_receiver: Receiver<(usize, FastaSeq)>,
    align_sender: Sender<(usize, String, Vec<u8>)>,
    features: Arc<Vec<FeatureInfo>>,
    match_score: isize,
    mismatch_score: isize,
    gap_open: isize,
    gap_extend: isize,
    min_similarity: f32,
) -> usize {
    let mut count = 0;
    for (num, read) in seq_receiver {
        count += 1;
        let sid = (&read.id[1..]).to_string();
        eprintln!("Aligning {num} {sid}");
        let seq: String = read.seq;
        let result = do_feature_align(
            seq,
            false,
            &features,
            match_score,
            mismatch_score,
            gap_open,
            gap_extend,
            min_similarity,
        );
        let mut buffer = vec![];
        let mut wtr = csv::Writer::from_writer(buffer);
        wtr.write_record(&[
            "fid",
            "start",
            "end",
            "is_forward",
            "similarity",
            "mapped_base",
            "dna_match",
            "score",
            "is_aa",
            "allow_overlap",
            "alt_str",
            "Type",
        ])
        .unwrap();
        for row in result {
            wtr.serialize(&row);
        }
        let result = wtr.into_inner().unwrap();
        align_sender.send((num, sid, result)).unwrap();
    }
    debug_println!("All seq aligned {count}");
    drop(align_sender);
    count
}
pub fn fasta_feature_align(
    result_path: PathBuf,
    fasta_path: &Path,
    feature_path: &Path,
    match_score: isize,
    mismatch_score: isize,
    gap_open: isize,
    gap_extend: isize,
    min_similarity: f32,
    thread: usize,
) -> usize {
    let features = Arc::new(load_features(feature_path).unwrap());
    // let mut decoder = fasta::Decoder::new(&mut reader).unwrap();
    let mut reader = fasta::FastaReader::new(fasta_path);
    let (seq_sender, seq_receiver) = bounded::<(usize, FastaSeq)>(thread * 10);
    let (align_sender, align_receiver) = bounded::<(usize, String, Vec<u8>)>(thread * 10);
    let writer_thread = thread::spawn(move || write_align_result(align_receiver, &result_path));
    let mut align_threads = vec![];
    for num in 0..thread {
        let rr = seq_receiver.clone();
        let ws = align_sender.clone();
        let tf = features.clone();
        align_threads.push(thread::spawn(move || {
            align_consumer(
                rr,
                ws,
                tf,
                match_score,
                mismatch_score,
                gap_open,
                gap_extend,
                min_similarity,
            )
        }))
    }
    drop(align_sender);
    let mut seq_count = 0;
    for read in reader.into_iter() {
        seq_sender.send((seq_count, read)).unwrap();
        seq_count += 1;
        if seq_count % 500 == 0 {
            debug_eprintln!("Loaded {seq_count} sequences.");
        }
    }
    drop(seq_sender);
    let mut aligned_seq_count = 0;
    for t in align_threads {
        aligned_seq_count += t.join().unwrap();
    }
    assert_eq!(seq_count, aligned_seq_count);
    let write_count = writer_thread.join().unwrap();
    assert_eq!(seq_count, write_count);
    seq_count
}
