use flate2::read::MultiGzDecoder;
// use rayon::iter::plumbing::*;
// use rayon::iter::IntoParallelIterator;
// use rayon::split_producer::*;
use std::fs::File;
use std::fs::OpenOptions;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::string::String;

#[derive(PartialEq, Clone, Debug)]
pub struct FastaSeq {
    pub id: String,
    pub seq: String,
}

unsafe impl Send for FastaSeq {}
unsafe impl Sync for FastaSeq {}

impl FastaSeq {
    pub fn new(id: String, seq: Option<String>) -> Self {
        match seq {
            Some(s) => FastaSeq { id, seq: s },
            None => FastaSeq {
                id,
                seq: String::new(),
            },
        }
    }
    pub fn to_tuple(self) -> (String, String) {
        (self.id, self.seq)
    }
}
pub struct FastaReader {
    pub filepath: PathBuf,
    fileobj: Box<dyn BufRead>,
    buffer: String,
}

unsafe impl Send for FastaReader {}

impl Iterator for FastaReader {
    type Item = FastaSeq;
    fn next(&mut self) -> Option<Self::Item> {
        self.read()
    }
}

// impl ParallelIterator for FastaReader {
//     type Item = FastaSeq;

//     fn drive_unindexed<C>(&mut self, consumer: C) -> C::Result
//     where
//         C: UnindexedConsumer<Self::Item>,
//     {
//         match self.read() {
//             Some
//         }
//     }
// }

impl FastaReader {
    pub fn new(filepath: &Path) -> FastaReader {
        match filepath.extension() {
            Some(extension) => match extension.to_str() {
                Some("fasta") => (),
                Some("fa") => (),
                Some("gz") => match filepath.with_extension("").extension() {
                    Some(extension2) => match extension2.to_str() {
                        Some("fasta") => (),
                        Some("fa") => (),
                        _ => panic!(
                            "Fasta file {} extension is not illegal. File extension should be [.fasta.gz, .fa.gz, .fasta, .fa]",
                            filepath.display()
                        ),
                    },
                    None => panic!("Fasta file {} extension is not illegal. File extension should be [.fasta.gz, .fa.gz, .fasta, .fa]",
                    filepath.display()),
                },
                _ => panic!(
                    "Fasta file {} extension is not illegal. File extension should be [.fasta.gz, .fa.gz, .fasta, .fa]",
                    filepath.display()
                ),
            },
            None => panic!("Fasta file {} do not have extension.", filepath.display()),
        }
        let file: File = OpenOptions::new().read(true).open(filepath).unwrap();
        if filepath.extension().unwrap() == "gz" {
            FastaReader {
                filepath: PathBuf::from(filepath),
                fileobj: Box::new(BufReader::new(MultiGzDecoder::new(file))),
                buffer: String::new(),
            }
        } else {
            FastaReader {
                filepath: PathBuf::from(filepath),
                fileobj: Box::new(BufReader::new(file)),
                buffer: String::new(),
            }
        }
    }
    pub fn read(&mut self) -> Option<FastaSeq> {
        if self.buffer.len() == 0 {
            // 如果当前没有 header 则尝试读一行header
            let slen = self.fileobj.read_line(&mut self.buffer).unwrap();
            if slen == 0 {
                //如果读不到数据，返回None
                assert_eq!(
                    slen,
                    self.buffer.len(),
                    "{slen} {hlen}",
                    hlen = self.buffer.len()
                );
                return None;
            }
        };
        assert!(
            self.buffer.starts_with(">"),
            "Fasta header not starts with '>' {}.",
            self.buffer
        );
        let mut seq = FastaSeq::new(self.buffer.trim().to_string(), None);
        self.buffer.clear();
        loop {
            let slen = self.fileobj.read_line(&mut self.buffer).unwrap();
            if slen == 0 {
                break;
            } else {
                if self.buffer.starts_with(">") {
                    break;
                } else {
                    seq.seq.push_str(&self.buffer.trim());
                    self.buffer.clear();
                }
            }
        }
        Some(seq)
    }
}
