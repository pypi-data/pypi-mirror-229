use crate::utils::base_to_flag;

pub fn char_cmp_exactly(chr1: char, chr2: char) -> bool {
    if chr1 == chr2 {
        true
    } else {
        false
    }
}

pub fn char_cmp_case_insensitive(chr1: char, chr2: char) -> bool {
    if chr1.to_lowercase().to_string() == chr2.to_lowercase().to_string() {
        true
    } else {
        false
    }
}

pub fn base_flag_cmp(flag1: u8, flag2: u8) -> bool {
    if flag1 == 0 && flag2 == 0 {
        true
    } else {
        match flag1 & flag2 {
            0 => false,
            _ => true,
        }
    }
}

pub fn base_cmp(base1: char, base2: char) -> bool {
    base_flag_cmp(base_to_flag(base1).unwrap(), base_to_flag(base2).unwrap())
}
