use jed::JedFile;

fn main() {
    let contents = include_str!("../latch.jed");
    dbg!(JedFile::parse(contents));
}
