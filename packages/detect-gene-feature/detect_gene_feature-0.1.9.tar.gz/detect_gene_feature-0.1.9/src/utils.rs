use pyo3::prelude::*;
use std::rc::Rc;

#[derive(Debug)]
pub struct AlignerConfig {
    pub chr_match: isize,
    pub chr_mismatch: isize,
    pub gap_open: isize,
    pub gap_extend: isize,
    pub clip_5: isize,
    pub clip_3: isize,
}

impl Default for AlignerConfig {
    fn default() -> Self {
        Self {
            chr_match: 1,
            chr_mismatch: -1,
            gap_open: -3,
            gap_extend: -1,
            clip_5: -5,
            clip_3: -5,
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub enum Matrix {
    Vertical,   //Up
    Horizontal, //Left
    Score,      //Diagonal
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AlignType {
    ChrMatch,
    ChrMismatch,
    Insertion,
    Deletion,
}

#[derive(Debug, Clone, Copy)]
pub struct BaseAlign {
    pub upos1: usize,
    pub upos2: usize,
    pub umatrix: Matrix,
    pub pos1: usize,
    pub pos2: usize,
    pub matrix: Matrix,
    pub chr1: Option<char>,
    pub chr2: Option<char>,
    pub atype: AlignType,
}

impl BaseAlign {
    pub fn new(
        upos1: usize,
        upos2: usize,
        umatrix: Matrix,
        pos1: usize,
        pos2: usize,
        matrix: Matrix,
        chr1: Option<char>,
        chr2: Option<char>,
        mode: AlignType,
    ) -> Self {
        Self {
            upos1,
            upos2,
            umatrix,
            pos1,
            pos2,
            matrix,
            chr1,
            chr2,
            atype: mode,
        }
    }
}

pub fn print_matrix(label: &str, matrix: &Vec<Vec<isize>>) {
    println!("{}:", label);
    let row_count = matrix.len();
    assert_ne!(row_count, 0);
    let column_count = matrix[0].len();
    print!("{:>3}", "");
    for j in 0..column_count {
        print!("{:>8},", j);
    }
    println!("");
    for (i, row) in matrix.into_iter().enumerate() {
        print!("{:>3}", i);
        for cell in row {
            print!("{:>8},", cell);
        }
        println!("");
    }
}

pub fn align_path_to_align_map(
    align_path: &Vec<Rc<BaseAlign>>,
) -> (Vec<(String, usize, usize, char, char, char)>, String) {
    let mut cigar_list: Vec<String> = vec![];
    let mut current_atype: Option<AlignType> = None;
    let mut atype_count: usize = 0;
    let mut align_result: Vec<(String, usize, usize, char, char, char)> = Vec::new();
    for align in align_path {
        let mtype = match align.matrix {
            Matrix::Score => "diagonal",
            Matrix::Vertical => "up",
            Matrix::Horizontal => "left",
        };
        let atype = match align.atype {
            AlignType::ChrMatch => '|',
            AlignType::ChrMismatch => '*',
            AlignType::Insertion => ' ',
            AlignType::Deletion => ' ',
        };
        match current_atype {
            None => {
                current_atype = Some(align.atype);
                atype_count = 1;
            }
            Some(x) => {
                if x == align.atype {
                    atype_count += 1;
                } else {
                    let cigar_str: Option<String> = match current_atype {
                        Some(AlignType::ChrMatch) => Some(format!("{}=", atype_count)),
                        Some(AlignType::ChrMismatch) => Some(format!("{}X", atype_count)),
                        Some(AlignType::Insertion) => Some(format!("{}I", atype_count)),
                        Some(AlignType::Deletion) => Some(format!("{}D", atype_count)),
                        None => None,
                    };
                    cigar_list.push(cigar_str.unwrap());
                    current_atype = Some(align.atype);
                    atype_count = 1;
                }
            }
        }
        let chr1 = match align.chr1 {
            Some(x) => x,
            None => '-',
        };
        let chr2 = match align.chr2 {
            Some(x) => x,
            None => '-',
        };
        align_result.push((mtype.to_string(), align.pos1, align.pos2, chr1, chr2, atype))
    }
    if current_atype != None {
        let cigar_str: Option<String> = match current_atype {
            Some(AlignType::ChrMatch) => Some(format!("{}=", atype_count)),
            Some(AlignType::ChrMismatch) => Some(format!("{}X", atype_count)),
            Some(AlignType::Insertion) => Some(format!("{}I", atype_count)),
            Some(AlignType::Deletion) => Some(format!("{}D", atype_count)),
            None => None,
        };
        cigar_list.push(cigar_str.unwrap());
    }
    (align_result, cigar_list.join(""))
}

#[pyfunction]
pub fn print_align_map(max_score: isize, align_map: Vec<(String, usize, usize, char, char, char)>) {
    println!("{}", print_align_map_ref(max_score, &align_map));
}

pub fn print_align_map_ref(
    max_score: isize,
    align_map: &Vec<(String, usize, usize, char, char, char)>,
) -> String {
    let seq1_start = align_map.first().unwrap().1;
    let seq1_end = align_map.last().unwrap().1;
    assert!(seq1_start <= seq1_end);
    let seq2_start = align_map.first().unwrap().2;
    let seq2_end = align_map.last().unwrap().2;
    assert!((seq2_start <= seq2_end));
    let mut seq1_list: Vec<char> = vec![];
    let mut seq2_list: Vec<char> = vec![];
    let mut match_list: Vec<char> = vec![];
    for align in align_map {
        seq1_list.push(align.3);
        seq2_list.push(align.4);
        match_list.push(align.5);
    }
    let seq1 = format!(
        "{seq1_start:<5} {seq1} {seq1_end:>5}\tScore:{max_score}",
        seq1_start = seq1_start,
        seq1 = seq1_list.iter().collect::<String>(),
        seq1_end = seq1_end,
        max_score = max_score
    );
    let seqm = format!(
        "{blank:<5} {match} {blank:>5}",
        blank=' ',
        match=match_list.iter().collect::<String>(),
    );
    let seq2 = format!(
        "{seq2_start:<5} {seq2} {seq2_end:>5}",
        seq2_start = seq2_start,
        seq2 = seq2_list.iter().collect::<String>(),
        seq2_end = seq2_end,
    );
    format!("{}\n{}\n{}", seq1, seqm, seq2)
}

pub fn base_to_flag(base: char) -> Result<u8, String> {
    match base {
        'A' | 'a' => Ok(0b0001u8),             //<A: 1>
        'C' | 'c' => Ok(0b0100u8),             //<C: 4>
        'G' | 'g' => Ok(0b0010u8),             //<G: 2>
        'T' | 't' | 'U' | 'u' => Ok(0b1000u8), //<T: 8>
        'W' | 'w' => Ok(0b1001u8),             //<T|A: 9>
        'S' | 's' => Ok(0b0110u8),             //<C|G: 6>
        'M' | 'm' => Ok(0b0101u8),             //<C|A: 5>
        'K' | 'k' => Ok(0b1010u8),             //<T|G: 10>
        'R' | 'r' => Ok(0b0011u8),             //<G|A: 3>
        'Y' | 'y' => Ok(0b1100u8),             //<T|C: 12>
        'B' | 'b' => Ok(0b1110u8),             //<T|C|G: 14>
        'D' | 'd' => Ok(0b1011u8),             //<T|G|A: 11>
        'H' | 'h' => Ok(0b1101u8),             //<T|C|A: 13>
        'V' | 'v' => Ok(0b0111u8),             //<C|G|A: 7>
        'N' | 'n' => Ok(0b1111u8),             //<T|C|G|A: 15>
        'X' | 'x' | '-' | '.' => Ok(0b0000u8), //<0: 0>
        _ => Err(format!("Base {} is not a IUPAC nucleotide code.", base)),
    }
}

pub fn base_complementary(base: char) -> Result<char, String> {
    match base {
        'A' => Ok('T'),
        'a' => Ok('t'),
        'C' => Ok('G'),
        'c' => Ok('g'),
        'G' => Ok('C'),
        'g' => Ok('c'),
        'T' => Ok('A'),
        't' => Ok('a'),
        'W' => Ok('W'),
        'w' => Ok('w'),
        'S' => Ok('S'),
        's' => Ok('s'),
        'M' => Ok('K'),
        'm' => Ok('k'),
        'K' => Ok('M'),
        'k' => Ok('m'),
        'R' => Ok('Y'),
        'r' => Ok('y'),
        'Y' => Ok('R'),
        'y' => Ok('r'),
        'B' => Ok('V'),
        'b' => Ok('v'),
        'D' => Ok('H'),
        'd' => Ok('h'),
        'H' => Ok('D'),
        'h' => Ok('d'),
        'V' => Ok('B'),
        'v' => Ok('b'),
        'N' => Ok('N'),
        'n' => Ok('n'),
        'X' => Ok('X'),
        'x' => Ok('x'),
        '-' => Ok('-'),
        '.' => Ok('.'),
        _ => Err(format!("Base {} is not a IUPAC nucleotide code.", base)),
    }
}

pub fn sequence_reverse_complement(seq: &str) -> String {
    let mut src = Vec::new();
    for chr in seq.chars().into_iter() {
        match base_complementary(chr) {
            Ok(x) => src.push(x.to_string()),
            Err(e) => panic!("{} in {}", e, seq),
        }
    }
    src.reverse();
    src.join("")
}

pub fn codon_to_amino_acid(codon: &str) -> Result<char, String> {
    // name "Standard" ,
    // name "SGC0"
    match codon {
        "TAA" | "TAG" | "TGA" | "taa" | "tag" | "tga" => Ok('*'),
        "GCA" | "GCC" | "GCG" | "GCT" | "gca" | "gcc" | "gcg" | "gct" => Ok('A'),
        "TGC" | "TGT" | "tgc" | "tgt" => Ok('C'),
        "GAC" | "GAT" | "gac" | "gat" => Ok('D'),
        "GAA" | "GAG" | "gaa" | "gag" => Ok('E'),
        "TTC" | "TTT" | "ttc" | "ttt" => Ok('F'),
        "GGA" | "GGC" | "GGG" | "GGT" | "gga" | "ggc" | "ggg" | "ggt" => Ok('G'),
        "CAC" | "CAT" | "cac" | "cat" => Ok('H'),
        "ATA" | "ATC" | "ATT" | "ata" | "atc" | "att" => Ok('I'),
        "AAA" | "AAG" | "aaa" | "aag" => Ok('K'),
        "CTA" | "CTC" | "CTG" | "CTT" | "TTA" | "TTG" | "cta" | "ctc" | "ctg" | "ctt" | "tta"
        | "ttg" => Ok('L'),
        "ATG" | "atg" => Ok('M'),
        "AAC" | "AAT" | "aac" | "aat" => Ok('N'),
        "CCA" | "CCC" | "CCG" | "CCT" | "cca" | "ccc" | "ccg" | "cct" => Ok('P'),
        "CAA" | "CAG" | "caa" | "cag" => Ok('Q'),
        "AGA" | "AGG" | "CGA" | "CGC" | "CGG" | "CGT" | "aga" | "agg" | "cga" | "cgc" | "cgg"
        | "cgt" => Ok('R'),
        "AGC" | "AGT" | "TCA" | "TCC" | "TCG" | "TCT" | "agc" | "agt" | "tca" | "tcc" | "tcg"
        | "tct" => Ok('S'),
        "ACA" | "ACC" | "ACG" | "ACT" | "aca" | "acc" | "acg" | "act" => Ok('T'),
        "GTA" | "GTC" | "GTG" | "GTT" | "gta" | "gtc" | "gtg" | "gtt" => Ok('V'),
        "TGG" | "tgg" => Ok('W'),
        "TAC" | "TAT" | "tac" | "tat" => Ok('Y'),
        _ => Err(format!("Input string {} is not a valid codon.", codon)),
    }
}

pub fn translate_dna(dna: &str) -> String {
    let mut aa_seq: Vec<char> = Vec::new();
    for idx in (0..dna.len()).step_by(3) {
        if idx + 3 <= dna.len() {
            // println!(
            //     "{} {} {}",
            //     idx,
            //     &dna[idx..idx + 3],
            //     codon_to_amino_acid(&dna[idx..idx + 3]).unwrap()
            // );
            aa_seq.push(codon_to_amino_acid(&dna[idx..idx + 3]).unwrap());
        }
    }
    aa_seq.iter().collect()
}
