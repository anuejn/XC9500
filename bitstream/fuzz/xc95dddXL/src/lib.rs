pub mod database;
pub mod bitstream;

use bitvec::prelude::BitVec;
use jed::JedFile;

#[derive(Debug, serde::Deserialize, Clone, Copy)]
pub struct Loc {
    pub fb: u8,
    pub mc: u8
}

#[derive(Debug, serde::Deserialize, Clone, Copy)]
pub enum Bit {
    Zero,
    One
}

macro_rules! impl_partial_eq {
    ($($ty:ty),*) => {
        $(
            impl PartialEq<Bit> for $ty {
                fn eq(&self, other: &Bit) -> bool {
                    self.eq(if matches!(other, Bit::One) { &1 } else { &0 })
                }
            }
        )*
    }
}

impl_partial_eq!(u8, u16, u32, u64, usize, i8, i16, i32, i64, isize);

#[derive(Debug, Clone, Copy)]
pub enum Device {
    XC9536XL,
    XC9572XL,
    XC95144XL,
    XC95288XL,
}

fn create_array<T, F: Fn(usize) -> T, const N: usize>(func: F) -> [T; N] {
    unsafe {
        let mut arr: [T; N] = std::mem::uninitialized();
        for (i, item) in (&mut arr[..]).into_iter().enumerate() {
            std::ptr::write(item, func(i));
        }
        arr
    }
}
