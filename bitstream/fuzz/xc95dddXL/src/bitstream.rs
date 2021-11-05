use bitvec::{BitArr, field::BitField, bitarr};
use bitvec::order::Msb0;
use bitvec::prelude::*;
use jed::JedFile;
use crate::{Bit, Loc, database::{DB, ImuxInput}, Device, create_array};

#[derive(Debug)]
pub struct RawBitStream {
    function_blocks: Vec<RawFunctionBlock>
}

impl RawBitStream {
    pub fn from_jed_file(jed: JedFile) -> Self {
        let n_fbs = jed.number_of_fuses / 108 / 108;
        let fuses = jed.fuses.values;

        let mut fbs = vec![];
        for fb in 0..n_fbs {
            let mut fb_fuses = BitVec::repeat(false, 108 * 108);
            for bit in 0..(108 * 108) {
                /*
                L0000000 00000000 00000000*
                L0000016 00000000 00000000*
                L0000032 00000000 00000000*
                L0000048 00000000 00000000*
                L0000064 00000000 00000000*
                L0000080 00000000 00000000*
                L0000096 00000000 00000000*
                L0000112 00000000 00000000*
                L0000128 00000000 00000000*
                L0000144 000000 000000*
                L0000156 000000 000000*
                L0000168 000000 000000*
                L0000180 000000 000000*
                L0000192 000000 000000*
                L0000204 000000 000000*
                */

                let row = bit / 108;
                let col = bit % 108;

                let mut target = n_fbs * row * 108;
                if col < (8 * 9) {
                    target += (col / 8) * 8 * n_fbs + 8 * fb + col % 8;
                } else {
                    let col = col - 8 * 9;
                    target += 8 * 9 * n_fbs + (col / 6) * 6 * n_fbs + 6 * fb + col % 6;
                }

                *fb_fuses.get_mut(bit).unwrap() = fuses[target];
            }

            fbs.push(RawFunctionBlock {
                fb: fb as u8,
                fuses: fb_fuses
            });
        }

        Self {
            function_blocks: fbs
        }
    }
}

#[derive(Debug)]
pub struct RawFunctionBlock {
    fb: u8,
    fuses: BitVec
}

#[derive(Debug)]
pub struct BitStream {
    pub usercode: [u8; 4],
    pub device: Device,
    pub function_blocks: Vec<FunctionBlock>
}

impl Device {
    fn from_number_of_function_blocks(nfb: usize) -> Self {
        match nfb {
            2 => Self::XC9536XL,
            4 => Self::XC9572XL,
            8 => Self::XC95144XL,
            16 => Self::XC95288XL,
            _ => unimplemented!()
        }
    }
}

impl BitStream {
    pub fn from_file(filename: &str) -> anyhow::Result<Self> {
        let jed = JedFile::parse(&std::fs::read_to_string(filename)?)?;
        let raw = RawBitStream::from_jed_file(jed);
        Ok(BitStream::from_raw(raw))
    }

    pub fn from_raw(raw_bitstream: RawBitStream) -> Self {
        let device = Device::from_number_of_function_blocks(raw_bitstream.function_blocks.len());

        Self {
            device,
            usercode: Self::parse_usercode(device, &raw_bitstream),
            function_blocks: raw_bitstream.function_blocks.into_iter().map(|fb| {
                FunctionBlock::from_raw(device, fb)
            }).collect(),
        }
    }

    fn parse_usercode(device: Device, raw_bitstream: &RawBitStream) -> [u8; 4] {
        let mut bits = BitVec::<Msb0>::with_capacity(8 * 4);
        for bit in DB.global_for(device).usercode {
            bits.push(raw_bitstream.function_blocks[0].fuses[bit as usize]);
        }
        [
            bits[0 * 8..1 * 8].load(),
            bits[1 * 8..2 * 8].load(),
            bits[2 * 8..3 * 8].load(),
            bits[3 * 8..4 * 8].load(),
        ]
    }
}

#[derive(Debug)]
pub struct FunctionBlock {
    pub macrocells: [MacroCell; 18],
    pub imux: [Option<ImuxSource>; 54]
}

impl FunctionBlock {
    fn from_raw(device: Device, raw: RawFunctionBlock) -> Self {
        Self {
            imux: Self::parse_imux(device, &raw),
            macrocells: create_array(|i| {
                MacroCell::from_raw(i, &raw)
            })
        }
    }

    fn parse_imux(device: Device, raw: &RawFunctionBlock) -> [Option<ImuxSource>; 54] {
        let mut configs = [None; 54];
        for pterm in 0..54 {
            let mut bits = bitarr![0; 5];
            // TODO(robin): should this be in the database??
            let row = pterm % 27 + 50;
            let off = pterm / 27;
            for bit in 0..5 {
                *bits.get_mut(bit).unwrap() = raw.fuses[108 * row + off + 6 + 8 * bit];
            }
            let config: usize = bits[..5].load();
            if config != 0 {
                configs[pterm] = Some(DB.imux_for(device).0[pterm][config].into());
            }
        }

        configs
    }
}

#[derive(Debug)]
pub enum SlewMode {
    Slow,
    Fast
}

#[derive(Debug)]
pub struct FFConfig {
    init: Bit,
    ty: FFType
}

#[derive(Debug)]
pub enum FFType {
    T,
    D
}

#[derive(Debug)]
pub struct MacroCell {
    pub slew_mode: SlewMode,
    pub ff: FFConfig,
    pub pterm1: AndArrayConfig,
    pub pterm2: AndArrayConfig,
    pub pterm3: AndArrayConfig,
    pub pterm4: AndArrayConfig,
    pub pterm5: AndArrayConfig,
}

macro_rules! parse_bit_pattern {
    ($raw:ident, $mc:ident, [$($bit:expr),*], { $($value:expr => $mapping:expr),* }) => {
        {
            let offset = DB.macrocell_offsets[$mc] as usize;
            let mut value = 0;
            let mut p = 0;
            $(
                value = value << 1;
                value |= if $raw.fuses[108 * ($bit as usize) + offset] { 1 } else { 0 };
                p += 1;
            )*

            let result = if false {
                unreachable!()
            }
            $(
                else if value == $value {
                    $mapping
                }
            )*
            else {
                unreachable!()
            };

            result
        }
    }
}

impl MacroCell {
    fn from_raw(i: usize, raw: &RawFunctionBlock) -> Self {
        let pterm1 = AndArrayConfig::from_raw(&raw, DB.pterm_offsets.offset_1[i]);
        let pterm2 = AndArrayConfig::from_raw(&raw, DB.pterm_offsets.offset_2[i]);
        let pterm3 = AndArrayConfig::from_raw(&raw, DB.pterm_offsets.offset_3[i]);
        let pterm4 = AndArrayConfig::from_raw(&raw, DB.pterm_offsets.offset_4[i]);
        let pterm5 = AndArrayConfig::from_raw(&raw, DB.pterm_offsets.offset_5[i]);

        let slew_mode = parse_bit_pattern!(raw, i, [DB.macrocell.slew_mode.bit], {
            DB.macrocell.slew_mode.config.slow => SlewMode::Slow,
            DB.macrocell.slew_mode.config.fast => SlewMode::Fast
        });

        let ff_init = parse_bit_pattern!(raw, i, [DB.macrocell.ff_init.bit], {
            DB.macrocell.ff_init.config.one => Bit::One,
            DB.macrocell.ff_init.config.zero => Bit::Zero
        });

        let ff_type = parse_bit_pattern!(raw, i, [DB.macrocell.ff_type.bit], {
            DB.macrocell.ff_type.config.t => FFType::T,
            DB.macrocell.ff_type.config.d => FFType::D
        });

        MacroCell {
            slew_mode,
            ff: FFConfig { init: ff_init, ty: ff_type },
            pterm1,
            pterm2,
            pterm3,
            pterm4,
            pterm5
        }
    }
}

#[derive(Debug)]
pub struct AndArrayConfig {
    pub normal: BitArr!(for 54),
    pub inverted: BitArr!(for 54),
}

impl AndArrayConfig {
    fn from_raw(raw: &RawFunctionBlock, offset: u16) -> Self {
        let offset = offset as usize;
        let mut normal = bitarr![0; 54];
        let mut inverted = bitarr![0; 54];
        for bit in 0..54 {
            *inverted.get_mut(bit).unwrap() = raw.fuses[108 * (2 * bit + 0) + offset];
            *normal.get_mut(bit).unwrap() = raw.fuses[108 * (2 * bit + 1) + offset];
        }

        Self {
            normal,
            inverted
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub enum ImuxSource {
    Feedback(Loc),
    Input(Loc)
}

impl From<ImuxInput> for ImuxSource {
    fn from(input: ImuxInput) -> ImuxSource {
        match input {
            ImuxInput::Feedback(loc) => Self::Feedback(loc),
            ImuxInput::Input(loc) => Self::Input(loc),
            ImuxInput::Unconnected => unreachable!()
        }
    }
}
