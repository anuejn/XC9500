use bitvec::order::Lsb0;
use bitvec::prelude::BitVec;

#[derive(Debug, Copy, Clone)]
pub enum Bit {
    Zero,
    One,
}

impl From<Bit> for bool {
    fn from(bit: Bit) -> Self {
        matches!(bit, Bit::One)
    }
}

#[derive(Debug)]
pub struct Fuses {
    pub default_state: Option<Bit>,
    pub values: BitVec,
    pub checksum: u16
}

#[derive(Debug)]
pub struct DeviceIdentification {
    pub architecture_code: usize,
    pub pinout_code: usize,
}

#[derive(Debug)]
pub struct TestVectors {
    pub default_condition: Option<Bit>
}

#[derive(Debug)]
pub struct JedFile {
    // stuff before the STX
    pub prefix: String,
    // stuff after the ETX and the checksum
    pub postfix: String,
    pub notes: Vec<String>,
    pub number_of_fuses: usize,
    pub number_of_pins: Option<usize>,
    pub number_of_test_vectors: Option<usize>,
    pub fuses: Fuses,
    pub device_identification: Option<DeviceIdentification>,
    pub test_vectors: TestVectors,
    pub checksum: u16,
}

#[derive(thiserror::Error, Debug)]
pub enum JedParserError {
    #[error("file does not contain <STX>, is this a valid jed file?")]
    MissingSTX,
    #[error("file does not contain <ETX>, is this a valid jed file?")]
    MissingETX,
    #[error("file contains `{0}` instead of valid checksum after <ETX>")]
    MissingChecksum(String),
    #[error("file contains `{0}` instead of valid checksum after <ETX>")]
    InvalidChecksum(String),
    #[error("a value field `Q` was found without a subfield")]
    InvalidValueField,
    #[error("the subfield `{0}` for a value field (`Q`) is unknown")]
    InvalidValueSubField(String),
    #[error("the fuse default `{0}` is not a valid binary number")]
    InvalidFuseDefault(String),
    #[error("the default test condition `{0}` is not a valid binary number")]
    InvalidTestConditionDefault(String),
    #[error("the device identification is not two decimal numbers seperated by space: `{0}`")]
    InvalidDeviceIdentification(String),
    #[error("the fuse specification did contain only a location: `{0}`")]
    InvalidFuseSpecification(String),
    #[error("unknown field identifier: `{0}`")]
    UnknownFieldIdentifier(String),
    #[error("invalid decimal number `{0}`")]
    InvalidNumber(String),
    #[error("invalid hexadecimal number `{0}`")]
    InvalidHexNumber(String),
    #[error("invalid bit `{0}`")]
    InvalidBit(String),
    #[error("did not find a terminating `*` for field `{0}`")]
    UnfinishedField(String)
}

struct JedParsingSystem<'a> {
    contents: &'a str,
    pos: usize,
}

impl<'a> JedParsingSystem<'a> {
    fn new(contents: &'a str) -> Self {
        JedParsingSystem {
            contents,
            pos: 0
        }
    }

    fn read_delimiter(&mut self) {
        while self.peek() == Some(" ") || self.peek() == Some("\n") {
            self.pop();
        }
    }

    // either returns the field identifier + field character or the unparsable part
    fn read_field<'b>(&'b mut self) -> Result<(&'a str, &'a str), &'a str> {
        self.read_delimiter();
        let field_identifier = self.pop();
        match field_identifier {
            Some(field_identifier) => {
                let mut p = self.pos;
                while p < self.contents.len() && &self.contents[p..p+1] != "*" {
                    p += 1;
                }
                if p == self.contents.len() {
                    Err(&self.contents[self.pos..p])
                } else {
                    let start = self.pos;
                    self.pos = p + 1;
                    Ok((field_identifier, &self.contents[start..self.pos - 1]))
                }
            },
            None => {
                Err("")
            }
        }
    }

    fn peek(&self) -> Option<&str> {
        if self.pos < self.contents.len() {
            Some(&self.contents[self.pos..self.pos + 1])
        } else {
            None
        }
    }

    fn pop<'b>(&'b mut self) -> Option<&'a str> {
        if self.pos < self.contents.len() {
            self.pos += 1;
            Some(&self.contents[self.pos - 1..self.pos])
        } else {
            None
        }
    }
}

impl JedFile {
    pub fn parse(contents: &str) -> Result<Self, JedParserError> {
        const STX: char = 2 as char;
        const ETX: char = 3 as char;
        // the actual jed file starts with <STX> and ends with the checksum after a <ETX>
        // many programs put some comment like thing before the <STX>
        let mut split = contents.splitn(2, STX);
        let prefix = split.next().unwrap();
        let contents = split.next().ok_or(JedParserError::MissingSTX)?;
        let mut split = contents.splitn(2, ETX);
        let commands = split.next().unwrap();
        let rest = split.next().ok_or(JedParserError::MissingETX)?;

        if rest.len() < 4 {
            return Err(JedParserError::MissingChecksum(rest.to_owned()));
        } else {
            let checksum = u16::from_str_radix(&rest[..4], 16).map_err(|_| JedParserError::InvalidChecksum(rest[..4].to_owned()))?;
            let mut parser = JedParsingSystem::new(commands);

            fn read_number(chars: &str) -> Result<usize, JedParserError> {
                usize::from_str_radix(&chars, 10)
                    .map_err(|_| JedParserError::InvalidNumber(chars.to_owned()))
            }

            fn read_hex_number(chars: &str) -> Result<usize, JedParserError> {
                usize::from_str_radix(&chars, 16)
                    .map_err(|_| JedParserError::InvalidHexNumber(chars.to_owned()))
            }

            fn read_bit(chars: &str) -> Result<Bit, JedParserError> {
                match &chars[..1] {
                    "0" => Ok(Bit::Zero),
                    "1" => Ok(Bit::One),
                    _ => Err(JedParserError::InvalidBit(chars.to_owned()))
                }
            }

            let mut fuses = BitVec::<Lsb0>::new();
            let mut number_of_fuses = None;
            let mut number_of_pins = None;
            let mut number_of_test_vectors = None;
            let mut default_fuse_value = None;
            let mut default_test_condition = None;
            let mut device_identification = None;
            let mut notes = Vec::new();
            let mut fuse_checksum = 0;

            loop {
                match parser.read_field() {
                    Ok((field_identifier, field_characters)) => {
                        match field_identifier {
                            "Q" => {
                                if field_characters.len() == 0 {
                                    return Err(JedParserError::InvalidValueField)
                                } else {
                                    match &field_characters[0..1] {
                                        "F" => {
                                            let n_fuses = read_number(&field_characters[1..])?;
                                            number_of_fuses = Some(n_fuses);
                                            fuses.reserve(n_fuses);
                                        },
                                        "P" => number_of_pins = Some(read_number(&field_characters[1..])?),
                                        "V" => number_of_test_vectors = Some(read_number(&field_characters[1..])?),
                                        unk => {
                                            return Err(JedParserError::InvalidValueSubField(unk.to_owned()))
                                        }
                                    }
                                }
                            },
                            "F" => {
                                if field_characters.len() != 1 {
                                    return Err(JedParserError::InvalidFuseDefault(field_characters.to_owned()))
                                } else {
                                    let default = read_bit(field_characters)?;
                                    default_fuse_value = Some(default);
                                    fuses = BitVec::repeat(default.into(), number_of_fuses.unwrap());
                                }
                            },
                            "X" => {
                                if field_characters.len() != 1 {
                                    return Err(JedParserError::InvalidTestConditionDefault(field_characters.to_owned()))
                                } else {
                                    default_test_condition = Some(read_bit(field_characters)?)
                                }
                            },
                            "J" => {
                                let parts: Vec<_> = field_characters.split(' ').collect();
                                if parts.len() != 2 {
                                    return Err(JedParserError::InvalidDeviceIdentification(field_characters.to_owned()));
                                } else {
                                    device_identification = Some(DeviceIdentification {
                                        architecture_code: read_number(parts[0])?,
                                        pinout_code: read_number(parts[1])?
                                    });
                                }
                            },
                            "N" => {
                                notes.push(field_characters.to_owned())
                            },
                            "L" => {
                                let mut start = 0;
                                while start < field_characters.len()
                                    && &field_characters[start..start+1] != " "
                                    && &field_characters[start..start+1] != "\n" {
                                    start += 1;
                                }
                                if start == field_characters.len() {
                                    return Err(JedParserError::InvalidFuseSpecification(field_characters.to_owned()));
                                } else {
                                    let location = read_number(&field_characters[..start])?;
                                    let mut pos = start;
                                    let mut bit = 0;
                                    while pos < field_characters.len() {
                                        match &field_characters[pos..pos+1] {
                                            "0" => {
                                                *fuses.get_mut(location + bit).unwrap() = false;
                                                bit += 1;
                                            },
                                            "1" => {
                                                *fuses.get_mut(location + bit).unwrap() = true;
                                                bit += 1;
                                            },
                                            " " | "\n" => {},
                                            _ => {
                                                return Err(JedParserError::InvalidFuseSpecification(field_characters.to_owned()));
                                            }
                                        }
                                        pos += 1;
                                    }
                                }
                            },
                            "C" => {
                                fuse_checksum = read_hex_number(field_characters)? as u16;
                            }
                            unk => {
                                return Err(JedParserError::UnknownFieldIdentifier(unk.to_owned()))
                            }
                        }
                    },
                    Err(rest) => {
                        if rest.len() == 0 {
                            break
                        } else {
                            return Err(JedParserError::UnfinishedField(rest.to_owned()))
                        }
                    }
                }
            }

            Ok(JedFile {
                prefix: prefix.to_owned(),
                postfix: (&rest[4..]).to_owned(),
                notes,
                number_of_fuses: number_of_fuses.unwrap(),
                number_of_pins,
                number_of_test_vectors,
                fuses: Fuses {
                    default_state: default_fuse_value,
                    values: fuses,
                    checksum: fuse_checksum
                },
                device_identification,
                test_vectors: TestVectors { default_condition: default_test_condition },
                checksum,
            })
        }
    }
}
