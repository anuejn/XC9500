use serde::Deserialize;
use crate::{Bit, Device, Loc};
use crate::bitstream::RawFunctionBlock;

lazy_static::lazy_static! {
    pub static ref DB: Database = serde_json::from_str(include_str!("../../../database.json")).unwrap();
}

#[derive(Debug, serde::Deserialize)]
pub struct Database {
    pub pterm_offsets: PtermOffsets,
    global: PerDevice<Global>,
    pub macrocell_offsets: [u16; 18],
    pub macrocell: Macrocell,
    imux: PerDevice<Imux>
}

impl Database {
    pub(crate) fn global_for(&self, device: Device) -> &Global {
        self.global.for_device(device)
    }

    pub(crate) fn imux_for(&self, device: Device) -> &Imux {
        self.imux.for_device(device)
    }
}

#[derive(Debug, serde::Deserialize)]
pub struct PtermOffsets {
    pub offset_1: [u16; 18],
    pub offset_2: [u16; 18],
    pub offset_3: [u16; 18],
    pub offset_4: [u16; 18],
    pub offset_5: [u16; 18],
}

// global clock, set/reset, oe, etc
#[derive(Debug, serde::Deserialize)]
pub(crate) struct Global {
    pub(crate) usercode: [u16; 32],
}

#[derive(Debug, serde::Deserialize)]
pub struct SingleBitValue<T> {
    pub bit: u16,
    #[serde(flatten)]
    pub config: T
}

#[derive(Debug, serde::Deserialize)]
pub struct SlewMode {
    pub fast: Bit,
    pub slow: Bit
}

#[derive(Debug, serde::Deserialize)]
pub struct FFInit {
    pub zero: Bit,
    pub one: Bit,
}

#[derive(Debug, serde::Deserialize)]
pub struct FFType {
    pub t: Bit,
    pub d: Bit,
}

#[derive(Debug, serde::Deserialize)]
pub struct Macrocell {
    pub slew_mode: SingleBitValue<SlewMode>,
    pub ff_init: SingleBitValue<FFInit>,
    pub ff_type: SingleBitValue<FFType>,
}

#[derive(Debug, serde::Deserialize)]
struct PerDevice<T> {
    xc9536xl: T,
    xc9572xl: T,
    xc95144xl: T,
    xc95288xl: T,
}

impl<T> PerDevice<T> {
    fn for_device(&self, device: Device) -> &T {
        match device {
            Device::XC9536XL => &self.xc9536xl,
            Device::XC9572XL => &self.xc9572xl,
            Device::XC95144XL => &self.xc95144xl,
            Device::XC95288XL => &self.xc95288xl,
        }
    }
}

// makes big arrays work
#[serbia::serbia]
#[derive(Debug, serde::Deserialize)]
pub struct Imux(// 54 entries, one for each pterm
    pub [[ImuxInput; 32]; 54]
);

#[derive(Debug, serde::Deserialize, Clone, Copy)]
#[serde(tag="type")]
pub enum ImuxInput {
    #[serde(rename="NC")]
    Unconnected,
    #[serde(rename="input")]
    Input(Loc),
    #[serde(rename="feedback")]
    Feedback(Loc)
}
