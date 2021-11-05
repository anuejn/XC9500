use xc95dddXL::bitstream::{AndArrayConfig, ImuxSource};

fn main() -> anyhow::Result<()> {
    let mut args = std::env::args();
    if args.len() != 2 {
        eprintln!("USAGE: {} <bitstream.jed>", args.nth(0).unwrap());
    } else {
        let bitstream = xc95dddXL::bitstream::BitStream::from_file(&args.nth(1).unwrap())?;
        println!("DEVICE {:?}", bitstream.device);
        println!("USERCODE {}", String::from_utf8(bitstream.usercode.to_vec())?);
        for (i, fb) in bitstream.function_blocks.iter().enumerate() {
            println!("FUNCTIONBLOCK {}", i);
            for (nmc, mc) in fb.macrocells.iter().enumerate() {
                println!("MACROCELL {}", nmc);
                println!("PTERM1: {}", dump_pterm_input(&fb.imux, &mc.pterm1));
                println!("PTERM2: {}", dump_pterm_input(&fb.imux, &mc.pterm2));
                println!("PTERM3: {}", dump_pterm_input(&fb.imux, &mc.pterm3));
                println!("PTERM4: {}", dump_pterm_input(&fb.imux, &mc.pterm4));
                println!("PTERM5: {}", dump_pterm_input(&fb.imux, &mc.pterm5));
                // println!("mc: {:?}", mc);
            }
        }
    }

    Ok(())
}

fn dump_pterm_input(imux_config: &[Option<ImuxSource>; 54], and_array_config: &AndArrayConfig) -> String {
    let mut ret = String::new();
    let mut is_first = true;

    fn first(first: &mut bool) -> &str {
        if !(*first) {
            " & "
        } else {
            *first = false;
            ""
        }
    }

    fn format_source(imux_config: &[Option<ImuxSource>; 54], i: usize) -> String {
        let source = imux_config[i].unwrap();
        match source {
            ImuxSource::Input(loc) => format!("FB_INPUT{}_{}", loc.fb, loc.mc),
            ImuxSource::Feedback(loc) => format!("FEEDBACK{}_{}", loc.fb, loc.mc)
        }
    }

    for (i, (normal, inverted)) in and_array_config.normal.iter().zip(&and_array_config.inverted).enumerate() {
        if *normal {
            ret += first(&mut is_first);
            ret += &format_source(&imux_config, i);
        }

        if *inverted {
            ret += first(&mut is_first);
            ret += "~";
            ret += &format_source(&imux_config, i);
        }
    }

    ret
}
