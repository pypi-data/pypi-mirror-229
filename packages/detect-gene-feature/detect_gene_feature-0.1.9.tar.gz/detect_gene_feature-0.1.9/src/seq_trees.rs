#![allow(unused)]
use crate::gotoh_local::{gotoh_local_align_all, gotoh_local_align_all_exact};
use crate::utils::print_align_map_ref;
use debug_print::debug_eprintln;
use bio::alphabets::dna;
use fnv::{FnvHashMap, FnvHashSet};
use protein_translate::translate;
use std::collections::{HashMap, HashSet};
use std::{cmp, vec};
use suffix::SuffixTable;
use debug_print::{self, debug_println};

type QueryHit=(usize, usize,usize);
#[derive(Debug)]
pub struct RawAlignResult{
        pub score:isize,
        pub mapped_base:usize,
        pub similarity:f32,
        pub ref_str:String,
        pub alt_str:String,
        pub ref_start:usize, 
        pub ref_end:usize, 
        pub alt_start:usize, 
        pub alt_end:usize,
        pub align_path:Vec<(String, usize, usize, char, char, char)>,
}

/// AlignResult(is_forward, score, match_count, 
///             simi, ref_str, alt_str, 
///             ref_start, ref_end, alt_start, alt_end)
#[derive(Debug)]
pub struct AlignResult {
    pub is_forward:bool,
    pub start:usize,
    pub end:usize,
    pub dna_match:usize,
    pub align:RawAlignResult
}


// assert_eq!(st.positions("quick"), &[4, 24]);
// assert!(st.contains("quick"));
#[derive()]
pub struct SeqTrees<'a> {
    pub seq_in: String,
    // pub dna_len: usize,
    // pub aa_len: usize,
    dna_seqs: Vec<String>,
    aa_seqs: Vec<String>,
    dna_tree: SuffixTable<'a, 'a>,
    dna_range: Vec<(usize, usize)>,
    aa_tree: SuffixTable<'a, 'a>,
    aa_range: Vec<(usize, bool, usize, usize)>,
}

impl<'a> SeqTrees<'a> {
    pub fn new(seq_in: String, liner:bool) -> Self {
        // let dna_len: usize = seq_in.len();
        let (seq_fw, seq_rc, dna_range)= if liner {
            let fw=seq_in.clone();
            let rc=String::from_utf8_lossy(&dna::revcomp(seq_in.as_bytes())).to_string();
            assert_eq!(fw.len(), rc.len());
            let range = vec![(0, seq_in.len()), (fw.len() + 1, fw.len()+1 +rc.len())];
            (fw,rc,range)
        }else{
            let fw=seq_in.clone() + &seq_in; //double seqin
            let rc=String::from_utf8_lossy(&dna::revcomp(fw.as_bytes())).to_string(); 
            assert_eq!(fw.len(), rc.len());
            let range = vec![(0, fw.len()), (fw.len() + 1, fw.len()+1 +rc.len())];
            (fw,rc,range)
        };
        // let seq_fw = seq_in.clone() + &seq_in; //double seqin
        // let seq_rc = String::from_utf8_lossy(&dna::revcomp(seq_fw.as_bytes())).to_string(); //double rc seqin
        let dna_tree = SuffixTable::new(seq_fw.clone() + "#" + &seq_rc);
        // let dna_range = vec![(0, dna_len * 2), (dna_len * 2 + 1, dna_len * 4 + 1)];
        // let aa_len: usize = (dna_len / 3) as usize + 1;
        let mut aa_seqs = vec![];
        let mut aa_range = vec![];
        let mut pre_len = 0;
        for idx in 0..3 {
            let aa_seq = translate(&seq_fw[idx..].as_bytes());
            // println!("{idx} FW {aa_seq}");
            aa_range.push((idx, true, pre_len, pre_len + aa_seq.len()));
            pre_len += aa_seq.len() + 1;
            aa_seqs.push(aa_seq);
            let rc_aa_seq = translate(&seq_rc[idx..].as_bytes());
            // println!("{idx} RC {rc_aa_seq}");
            aa_range.push((idx, false, pre_len, pre_len + rc_aa_seq.len()));
            pre_len += rc_aa_seq.len() + 1;
            aa_seqs.push(rc_aa_seq);
        }
        debug_print::debug_eprintln!("Seq {dlen}, FW {fwl}, RC {rcl}\nDNA Range:{range:?}\nAA Range:{aa_range:?}\n",
                                    dlen=seq_in.len(),
                                    fwl=seq_fw.len(), 
                                    rcl=seq_rc.len(), 
                                    range=dna_range,
                                    aa_range=aa_range);
        let aa_tree = SuffixTable::new(aa_seqs.join("#"));
        let dna_seqs = vec![seq_fw, seq_rc];
        SeqTrees {
            seq_in,
            // dna_len,
            // aa_len,
            dna_seqs,
            aa_seqs,
            dna_tree,
            dna_range,
            aa_tree,
            aa_range,
        }
    } 

    pub fn query_dna(&self, query: &str) -> Vec<QueryHit> {
        let (fw_start, fw_end) = self.dna_range[0];
        let (rc_start, rc_end) = self.dna_range[1];
        let mut hits = vec![];
        for start_u32 in self.dna_tree.positions(query) {
            let mut start = *start_u32 as usize;
            if fw_start <= start && start < fw_end {
                let end = start + query.len();
                let hit_seq = &self.dna_seqs[0][start..end];
                assert_eq!(query, hit_seq, "Forward {query} {hit_seq}"); //check query result correct.
                hits.push((0, start, end));
            } else {
                assert!(
                    rc_start <= start && start < rc_end,
                    "{fw_start} {fw_end} {rc_start} {rc_end} {start}"
                );
                start -= rc_start;
                let end = start + query.len();
                let hit_seq = &self.dna_seqs[1][start..end];
                assert_eq!(query, hit_seq, "Reverse {query} {hit_seq}"); //check query result correct.
                hits.push((1, start, end));
            };
        }
        hits
    }

    pub fn query_aa(&self, query: &str) -> Vec<QueryHit> {
        let (_, _, f0_start, f0_end) = &self.aa_range[0];
        let (_, _, r0_start, r0_end) = &self.aa_range[1];
        let (_, _, f1_start, f1_end) = &self.aa_range[2];
        let (_, _, r1_start, r1_end) = &self.aa_range[3];
        let (_, _, f2_start, f2_end) = &self.aa_range[4];
        let (_, _, r2_start, r2_end) = &self.aa_range[5];
        let mut hits = vec![];
        for start_u32 in self.aa_tree.positions(query) {
            let mut start = *start_u32 as usize;
            if *f0_start <= start && start < *f0_end {
                start -= f0_start;
                let end = start + query.len();
                let hit_seq = &self.aa_seqs[0][start..end];
                assert_eq!(query, hit_seq, "Forward {query} {hit_seq}"); //check query result correct.
                hits.push((0, start, end));
            } else if *r0_start <= start && start < *r0_end {
                start -= r0_start;
                let end = start + query.len();
                let hit_seq = &self.aa_seqs[1][start..end];
                assert_eq!(query, hit_seq, "Forward {query} {hit_seq}"); //check query result correct.
                hits.push((1, start, end));
            } else if *f1_start <= start && start < *f1_end {
                start -= f1_start;
                let end = start + query.len();
                let hit_seq = &self.aa_seqs[2][start..end];
                assert_eq!(query, hit_seq, "Forward {query} {hit_seq}"); //check query result correct.
                hits.push((2, start, end));
            } else if *r1_start <= start && start < *r1_end {
                start -= r1_start;
                let end = start + query.len();
                let hit_seq = &self.aa_seqs[3][start..end];
                assert_eq!(query, hit_seq, "Forward {query} {hit_seq}"); //check query result correct.
                hits.push((3, start, end));
            } else if *f2_start <= start && start < *f2_end {
                start -= f2_start;
                let end = start + query.len();
                let hit_seq = &self.aa_seqs[4][start..end];
                assert_eq!(query, hit_seq, "Forward {query} {hit_seq}"); //check query result correct.
                hits.push((4, start, end));
            } else if *r2_start <= start && start < *r2_end {
                start -= r2_start;
                let end = start + query.len();
                let hit_seq = &self.aa_seqs[5][start..end];
                assert_eq!(query, hit_seq, "Forward {query} {hit_seq}"); //check query result correct.
                hits.push((5, start, end));
            } else {
                panic!("Range Error {start} {range:#?}", range = self.aa_range);
            };
        }
        hits
    }

    pub fn align_dna(
        &self,
        query: &str,
        window: usize,
        flank_len: usize,
        chr_match: isize,
        chr_mismatch: isize,
        gap_open: isize,
        gap_extend: isize,
        min_simility: f32,
    ) -> Vec<AlignResult> {
        let mut fw_hits: Vec<(usize, usize)> = vec![];
        let mut rc_hits: Vec<(usize, usize)> = vec![];
        for idx in (0..query.len()-window) {
            if idx + window > query.len() {
                continue;
            } else {
                for (seq_id, start, end) in self.query_dna(&query[idx..idx + window]) {
                    let dna_len=self.dna_range[seq_id].1-self.dna_range[seq_id].0;
                    let rstart = cmp::max(0, start as isize - flank_len as isize) as usize;
                    let rend = cmp::min(dna_len, end + flank_len);
                    assert!(rstart < rend, "{seq_id} {start} {end} {rstart} {rend}");
                    // if rstart > self.dna_len {
                    //     //如果extend后的区间在一倍长度之后，则跳过。
                    //     continue;
                    // }
                    if seq_id == 0 {
                        fw_hits.push((rstart, rend));
                    } else {
                        rc_hits.push((rstart, rend));
                    }
                }
            }
        }
        fw_hits.sort();
        debug_eprintln!("Forward hits {:?}", fw_hits);
        let fw_hits_rmdup=dna_region_rmdup(&mut fw_hits, 
            true,
             self.seq_in.len());
        debug_eprintln!("Forward hits rmdup {:?}", fw_hits_rmdup);
        let mut align_result :Vec<AlignResult>=vec![];
        for ar in
            align_seq(
                query,
                &self.dna_seqs[0],
                fw_hits_rmdup,
                true,
                chr_match,
                chr_mismatch,
                gap_open,
                gap_extend,
                min_simility,
            )
        {
            align_result.push(AlignResult{is_forward:true,
                 start:ar.ref_start, 
                 end:ar.ref_end,
                 dna_match:ar.mapped_base, 
                 align:ar});
        }
        // println!("Forward hit {}.", align_result.len());
        rc_hits.sort();
        debug_eprintln!("Reverse hits {:?}", rc_hits);
        let rc_hits_rmdup=dna_region_rmdup(&mut rc_hits, 
            true, 
            self.seq_in.len());
        debug_eprintln!("Reverse hits rmdup {:?}", rc_hits_rmdup);
        for ar in
            align_seq(
                query,
                &self.dna_seqs[1],
                rc_hits_rmdup,
                true,
                chr_match,
                chr_mismatch,
                gap_open,
                gap_extend,
                min_simility,
            )
        {//命中到负链上
            let dna_len=self.dna_range[1].1-self.dna_range[1].0;
            let f_start = dna_len - ar.ref_end;
            let f_end = dna_len - ar.ref_start;
            debug_eprintln!("Reverse Align {} {} {} {} {}", dna_len, ar.ref_start, ar.ref_end, f_start, f_end);
            assert!(f_start < f_end,
                "Reverse align {dna_len} {ref_start} {ref_end} {f_start} {f_end} {alt_start} {alt_end} {ref_str} {alt_str}",
                dna_len=dna_len,
                ref_start=ar.ref_start,
                ref_end=ar.ref_end,
                alt_start=ar.alt_start,
                alt_end=ar.alt_end,
                ref_str=ar.ref_str,
                alt_str=ar.alt_str);
            // eprintln!("Reverse Align Position {astart} {aend} {f_start} {f_end}", astart=ar.ref_start, aend=ar.ref_end);
            let fw_rc =
                String::from_utf8_lossy(&dna::revcomp(self.dna_seqs[0][f_start..f_end].as_bytes()))
                    .to_string();
            let rc_seq = &self.dna_seqs[1][ar.ref_start..ar.ref_end];
            assert_eq!(
                fw_rc,
                rc_seq,
                "{dna_len} {ref_start} {ref_end} {f_start} {f_end} {fw_rc} {rc_seq} {ref_str}",
                dna_len = dna_len,
                ref_start=ar.ref_start,
                ref_end=ar.ref_end,
                ref_str=ar.ref_str);
            assert_eq!(
                fw_rc,
                ar.ref_str,
                "{dna_len} {ref_start} {ref_end} {f_start} {f_end} {fw_rc} {rc_seq} {ref_str}",
                dna_len = dna_len,
                ref_start=ar.ref_start,
                ref_end=ar.ref_end,
                ref_str=ar.ref_str);
            align_result.push(AlignResult{is_forward:false,
                                          start:f_start, 
                                          end:f_end,
                                          dna_match:ar.mapped_base,
                                          align:ar})
        }
        debug_eprintln!("Align Result {:?}", align_result);
        align_result
    }
    pub fn align_aa(
        &self,
        query: &str,
        query_dna_seq:&str,
        window: usize,
        flank_len: usize,
        chr_match: isize,
        chr_mismatch: isize,
        gap_open: isize,
        gap_extend: isize,
        min_simility: f32,
    ) -> Vec<AlignResult>{
        let mut seq_hit = FnvHashMap::default();
        for idx in (0..query.len()-window) {
            if idx + window > query.len() {
                continue;
            } else {
                for (seq_id, start, end) in self.query_aa(&query[idx..idx + window]) {
                    let aa_len=self.aa_range[seq_id].3-self.aa_range[seq_id].2;
                    let rstart = cmp::max(0, start as isize - flank_len as isize) as usize;
                    let rend = cmp::min(aa_len, end + flank_len);
                    assert!(rstart < rend, "{seq_id} {start} {end} {rstart} {rend}");
                    // if rstart > self.aa_len {
                    //     //如果extend后的区间在一倍长度之后，则跳过。
                    //     continue;
                    // }
                    let mut hits = seq_hit.entry(seq_id).or_insert(vec![]);
                    hits.push((rstart, rend));
                }
            }
        }
        let mut align_result :Vec<AlignResult>=vec![];
        for (seq_id, mut regions) in seq_hit.into_iter() {
            for ar in align_seq(query,
                &self.aa_seqs[seq_id],
                merge_regions(&mut regions, true),
                false,
                chr_match,
                chr_mismatch,
                gap_open,
                gap_extend,
                min_simility) {
                let (f_start, f_end, dna_match) = if self.aa_range[seq_id].1 {
                    // if aa seq is foward strand.
                    let start = self.aa_range[seq_id].0 + ar.ref_start * 3;
                    let end = self.aa_range[seq_id].0 + ar.ref_end * 3;
                    let hit_aa = translate(&self.dna_seqs[0][start..end].as_bytes());
                    assert_eq!(
                        ar.ref_str,
                        hit_aa,
                        "{seq_id} {seq_info:#?} {ref_start} {ref_end} {start} {end} {alt_start} {alt_end} {ref_str} {hit_aa}",
                        seq_info = self.aa_range[seq_id],
                        ref_start=ar.ref_start,
                        ref_end=ar.ref_end,
                        alt_start=ar.alt_start,
                        alt_end=ar.alt_end,
                        ref_str=ar.ref_str
                    );
                    let a_start=ar.alt_start*3;
                    let a_end=ar.alt_end*3;
                    let a_aa=translate(&query_dna_seq[a_start..a_end].as_bytes());
                    assert_eq!(a_aa, ar.alt_str, "{seq_id} {seq_info:#?} {ref_start} {ref_end} {start} {end} {alt_start} {alt_end} {a_start} {a_end} {a_aa} {hit_aa}",
                    seq_info = self.aa_range[seq_id],
                    ref_start=ar.ref_start,
                    ref_end=ar.ref_end,
                    alt_start=ar.alt_start,
                    alt_end=ar.alt_end);
                    let mut matched_base=0;
                    for (a,b) in ar.alt_str.as_bytes().iter().zip(query_dna_seq[a_start..a_end].as_bytes()){
                        if a==b{
                            matched_base+=1;
                        }
                    }
                    (start, end, matched_base)
                } else {
                    // if aa seq is reverse strand.
                    let dna_len=self.dna_range[0].1-self.dna_range[0].0;
                    let start = dna_len - (self.aa_range[seq_id].0 + ar.ref_end * 3);
                    let end = dna_len - (self.aa_range[seq_id].0 + ar.ref_start * 3);
                    assert!(end <= dna_len, 
                        "Position Error. {dna_len} {start} {end} {range:?} {astart} {aend}", 
                        range=self.aa_range[seq_id],
                        astart=ar.ref_start, 
                        aend=ar.ref_end);
                    let hit_aa = translate(&dna::revcomp(self.dna_seqs[0][start..end].as_bytes()));
                    assert_eq!(
                        ar.ref_str,
                        hit_aa,
                        "{seq_id} {seq_info:#?} {ref_start} {ref_end} {start} {end} {alt_start} {alt_end} {ref_str} {hit_aa}",
                        seq_info = self.aa_range[seq_id],
                        ref_start=ar.ref_start,
                        ref_end=ar.ref_end,
                        alt_start=ar.alt_start,
                        alt_end=ar.alt_end,
                        ref_str=ar.ref_str
                    );
                    let a_start=ar.alt_start*3;
                    let a_end=ar.alt_end*3;
                    let a_aa=translate(&query_dna_seq[a_start..a_end].as_bytes());
                    assert_eq!(a_aa, ar.alt_str, "{seq_id} {seq_info:#?} {ref_start} {ref_end} {start} {end} {alt_start} {alt_end} {a_start} {a_end} {a_aa} {hit_aa}",
                    seq_info = self.aa_range[seq_id],
                    ref_start=ar.ref_start,
                    ref_end=ar.ref_end,
                    alt_start=ar.alt_start,
                    alt_end=ar.alt_end);
                    let mut matched_base=0;
                    for (a,b) in ar.alt_str.as_bytes().iter().zip(query_dna_seq[a_start..a_end].as_bytes()){
                        if a==b{
                            matched_base+=1;
                        }
                    }
                    (start, end, matched_base)
                };
                assert!(f_start < f_end,
                "Reverse align {ref_start} {ref_end} {f_start} {f_end} {alt_start} {alt_end} {ref_str} {alt_str}",
                ref_start=ar.ref_start,
                ref_end=ar.ref_end,
                alt_start=ar.alt_start,
                alt_end=ar.alt_end,
                ref_str=ar.ref_str,
                alt_str=ar.alt_str);
                align_result.push(AlignResult{is_forward:self.aa_range[seq_id].1, 
                    start:f_start, 
                    end:f_end, 
                    dna_match:dna_match,
                    align:ar});
            }
        }
        // max_score_align_result(align_result)
        align_result
    }
}


pub fn merge_regions(regions: &mut Vec<(usize, usize)>, 
                     merge_adjacent: bool) -> Vec<(usize, usize)> {
    let (start_flag, end_flag) = match merge_adjacent {
        true => (0, 1),
        false => (1, 0),
    };
    let mut position_list: Vec<(usize, usize)> = vec![];
    regions.sort();
    for (start, end) in regions {
        position_list.push((*start, start_flag));
        position_list.push((*end, end_flag));
    }
    let mut merged_regions: Vec<(usize, usize)> = vec![];
    let mut start_count = 0;
    let mut rstart: Option<usize> = None;
    position_list.sort();
    for (pos, flag) in position_list {
        if flag == start_flag {
            start_count += 1;
            rstart = match rstart {
                None => {
                    assert_eq!(start_count, 1);
                    Some(pos)
                }
                Some(x) => Some(x),
            };
        } else {
            start_count -= 1;
            if start_count == 0 {
                // assert_eq!(rstart, None);
                merged_regions.push((rstart.expect("Someting Error."), pos));
                rstart = None;
            }
        }
    }
    merged_regions
}

fn dna_region_rmdup(regions: &mut Vec<(usize, usize)>, merge_adjacent: bool, seq_len:usize
    )->Vec<(usize, usize)>{
    let mut region_set =FnvHashSet::default();
    let regions= merge_regions(regions, merge_adjacent);
    for (start, end) in regions.iter(){
        if *start < seq_len{
            region_set.insert((*start,*end));
        } else{
            region_set.insert((*start-seq_len, *end-seq_len));
        }
    }
    let mut rmdup_regions =region_set.into_iter().collect::<Vec<(usize, usize)>>();
    rmdup_regions.sort();
    // println!("{} {} {:?}",  regions.len(), rmdup_regions.len(), rmdup_regions);
    rmdup_regions
}

pub fn align_seq(
    query: &str,  //feature sequence
    target: &str, //dna sequence
    target_regions: Vec<(usize, usize)>,
    is_dna: bool,
    chr_match: isize,
    chr_mismatch: isize,
    gap_open: isize,
    gap_extend: isize,
    min_simility: f32,
) -> Vec<RawAlignResult> {
    let aligner = match is_dna {
        true => gotoh_local_align_all,
        false => gotoh_local_align_all_exact,
    };
    let mut aligns = vec![];
    for (start, end) in target_regions {
        // println!("Merged region {:?} {}", start, end);
        let target_seq=target.get(start..end).expect(&format!("Out of Bounds {tlen} {start} {end}", tlen= target.len()));
        let (score, align_path) = aligner(
            target_seq,
            query,
            chr_match,
            chr_mismatch,
            gap_open,
            gap_extend,
        )
        .expect("Align Error.");
        for (apath, _acigar) in align_path {
            // print_align_map_ref(score, &apath);
            let mut mapped_base = 0usize;
            let mut ref_base = vec![];
            let mut alt_base = vec![];
            for n in &apath {
                if n.3 != '-' {
                    ref_base.push(n.3);
                };
                if n.4 != '-' {
                    alt_base.push(n.4);
                }
                if n.5 == '|' {
                    mapped_base += 1;
                };
            }
            let ref_start = apath[0].1 -1 + start; // 0 based
            let alt_start = apath[0].2 -1; //0 based
            let ref_end = apath[apath.len() - 1].1 + start; //target
            let alt_end = apath[apath.len() - 1].2; //query
            assert!(ref_start < ref_end, "{apath:?}");
            let similarity = mapped_base as f32 / (ref_end-ref_start) as f32;
            let similarity2 = mapped_base as f32 / query.len() as f32;
            if similarity > min_simility && similarity2 > min_simility {
                let ref_str: String = ref_base.iter().collect();
                let alt_str: String = alt_base.iter().collect();
                assert_eq!(
                    target[ref_start..ref_end],
                    ref_str,
                    "{query} {target} {ref_start} {ref_end} {alt_start} {alt_end} {ref_str} {alt_str}"
                );
                assert_eq!(query[alt_start..alt_end], 
                    alt_str, 
                    "{query} {target} {ref_start} {ref_end} {alt_start} {alt_end} {ref_str} {alt_str}");
                aligns.push(RawAlignResult{score,
                                mapped_base,
                                similarity,
                                ref_str,
                                alt_str,
                                ref_start, 
                                ref_end, 
                                alt_start, 
                                alt_end,
                                align_path:apath})
            }
        }
    }
    aligns
}

fn max_score_align_result(align_result: Vec<AlignResult>)->Vec<AlignResult>{
    let result_count=align_result.len();
    let mut max_score=isize::MIN;
    for result in align_result.iter(){
        debug_println!("Align Result: {} {} {} {}", result.is_forward, result.start, result.end, result.dna_match);
        if result.align.score > max_score{
            max_score=result.align.score
        }
    }
    let filtered_result:Vec<_>=align_result.into_iter().filter(|x| x.align.score==max_score).collect();
    // if filtered_result.len()< result_count{
    //     eprintln!("Filtered {result_count} {filtered_count}", filtered_count=filtered_result.len());
    // }
    filtered_result
}