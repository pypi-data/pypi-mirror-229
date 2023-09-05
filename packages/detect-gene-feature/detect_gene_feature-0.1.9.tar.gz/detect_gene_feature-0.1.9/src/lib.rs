pub mod char_compare;
pub mod fasta;
pub mod feature_align;
pub mod gotoh_local;
pub mod seq_trees;
pub mod utils;
use debug_print::debug_eprintln;
use crate::feature_align::{do_align_seq, AlignTuple, load_features, do_feature_align, FeatureInfo};
use pyo3::prelude::*;
use std::path::PathBuf;
/// Formats the sum of two numbers as string.
///
#[pyfunction]
fn load_feature(
    feature_path: String,
) -> PyResult<Vec<(String, String, bool, String, String, bool, u32)>> {
    let mut features = vec![];
    for feature in feature_align::load_features(&PathBuf::from(feature_path))
        .unwrap()
        .into_iter()
    {
        features.push(feature.to_tuple());
    }
    Ok(features)
}

#[pyfunction]
fn load_fasta(fasta_path: String) -> PyResult<Vec<(String, String)>> {
    let mut seqs = vec![];
    for seq in fasta::FastaReader::new(&PathBuf::from(fasta_path)) {
        seqs.push(seq.to_tuple())
    }
    Ok(seqs)
}

#[pyfunction]
fn align_seq(
    seq_in: String,
    liner: bool,
    query_dna: String,
    query_aa: String,
    is_aa: bool,
    match_score: Option<isize>,
    mismatch_score: Option<isize>,
    gap_open: Option<isize>,
    gap_extend: Option<isize>,
    min_similarity: Option<f32>,
) -> PyResult<Vec<(usize, usize, bool, f32, usize, usize, isize, String, String)>> {
    Ok(do_align_seq(
        seq_in,
        liner,
        query_dna,
        query_aa,
        is_aa,
        match_score.unwrap_or(1),
        mismatch_score.unwrap_or(-1),
        gap_open.unwrap_or(-3),
        gap_extend.unwrap_or(-1),
        min_similarity.unwrap_or(0.9),
    ))
}

///Suffix search sequence
#[pyfunction]
fn sequence_search(
    target: String,
    query: String,
    liner: bool,
    is_dna: bool,
    windows: Option<usize>,
) -> PyResult<Vec<(usize, Vec<(usize, usize, usize)>)>> {
    let windows=match windows {
        Some(x)=> x,
        None=> query.len(),
    };
    let st = seq_trees::SeqTrees::new(target, liner);
    let mut result: Vec<(usize, Vec<(usize, usize, usize)>)>=vec![];
    if is_dna {
        for(idx,sub) in query.chars().collect::<Vec<char>>().windows(windows).enumerate(){
            let sub_str:String=sub.into_iter().collect();
            let hits=st.query_dna(&sub_str);
            result.push((idx, hits));
        }
    } else {
        for(idx,sub) in query.chars().collect::<Vec<char>>().windows(windows).enumerate(){
            let sub_str:String=sub.into_iter().collect();
            // println!("{sub_str}");
            let hits=st.query_aa(&sub_str);
            result.push((idx, hits));
        }
    };
    result.sort();
    result.dedup();
    Ok(result)
}



#[pyfunction]
fn align_feature(
    seq_in: String,
    liner: bool,
    feature_path: String,
    match_score: Option<isize>,
    mismatch_score: Option<isize>,
    gap_open: Option<isize>,
    gap_extend: Option<isize>,
    min_similarity: Option<f32>,
) -> PyResult<Vec<AlignTuple>> {
    let features = load_features(&PathBuf::from(&feature_path)).unwrap();
    debug_eprintln!("{feature_path} feature loaded.");
    let ar=do_feature_align(
        seq_in,
        liner,
        &features,
        match_score.unwrap_or(1),
        mismatch_score.unwrap_or(-1),
        gap_open.unwrap_or(-3),
        gap_extend.unwrap_or(-1),
        min_similarity.unwrap_or(0.9),
    );
    PyResult::Ok(ar)
}

#[pyfunction]
fn align_feature_list(
    seq_in: String,
    liner: bool,
    feature_list: Vec<(String, String, bool, String, String, bool, u32)>,
    match_score: Option<isize>,
    mismatch_score: Option<isize>,
    gap_open: Option<isize>,
    gap_extend: Option<isize>,
    min_similarity: Option<f32>,
) -> PyResult<Vec<AlignTuple>> {
    let mut features=vec![];
    for f in feature_list{
        features.push(FeatureInfo::from_tuple(f))
    }
    let ar=do_feature_align(
        seq_in,
        liner,
        &features,
        match_score.unwrap_or(1),
        mismatch_score.unwrap_or(-1),
        gap_open.unwrap_or(-3),
        gap_extend.unwrap_or(-1),
        min_similarity.unwrap_or(0.9),
    );
    PyResult::Ok(ar)
}

#[pyfunction]
fn align_fasta(
    fasta_path: String,
    feature_path: String,
    result_path: Option<String>,
    match_score: Option<isize>,
    mismatch_score: Option<isize>,
    gap_open: Option<isize>,
    gap_extend: Option<isize>,
    min_similarity: Option<f32>,
    thread: Option<usize>,
) -> PyResult<usize> {
    let fasta_path = PathBuf::from(fasta_path);
    let result_path = match result_path {
        Some(x) => PathBuf::from(x),
        None => fasta_path.with_extension("features.zip"),
    };
    let sc = feature_align::fasta_feature_align(
        result_path,
        &fasta_path,
        &PathBuf::from(feature_path),
        match_score.unwrap_or(1),
        mismatch_score.unwrap_or(-1),
        gap_open.unwrap_or(-3),
        gap_extend.unwrap_or(-1),
        min_similarity.unwrap_or(0.9),
        thread.unwrap_or(20),
    );
    PyResult::Ok(sc)
}

/// A Python module implemented in Rust.
#[pymodule]
fn detect_gene_feature(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load_feature, m)?)?;
    m.add_function(wrap_pyfunction!(sequence_search, m)?)?;
    m.add_function(wrap_pyfunction!(align_feature, m)?)?;
    m.add_function(wrap_pyfunction!(align_feature_list, m)?)?;
    m.add_function(wrap_pyfunction!(align_fasta, m)?)?;
    m.add_function(wrap_pyfunction!(load_fasta, m)?)?;
    m.add_function(wrap_pyfunction!(align_seq, m)?)?;
    Ok(())
}
