#!/usr/bin/env python3

from switch import dump_html_for_tag
import infra.ise
from infra import jed
from pathlib import Path



# if __name__ == "__main__":
#     output = "FB1_2"
#     inputs = [f"FB1_{i}" for i in range(10,10+5)]
#     ucf = f'INST "inst" LOC="{output}"; NET "output" LOC="{output}"; NET "clk" LOC="15";' " ".join(f'NET "input{i + 1}" LOC="{inputs[i]}";' for i in range(len(inputs)))
#     VHDL = f"""
#         library IEEE;
#         use IEEE.STD_LOGIC_1164.ALL;
#         library unisim;
#         use UNISIM.vcomponents.ALL;
#
#         entity passthrough is
#             Port (clk : in STD_LOGIC; input1 : in STD_LOGIC; input2 : in STD_LOGIC; input3 : in STD_LOGIC; input4 : in STD_LOGIC; input5 : in STD_LOGIC; output: out STD_LOGIC);
#         end passthrough;
#
#         architecture Behavioral of passthrough is
#             signal D : STD_LOGIC;
#         begin
#             inst: LDCP
#             generic map (
#                 INIT => '0'
#             )
#             port map (
#                 Q => output,
#                 G => clk,
#                 CLR => '0',
#                 PRE => '0',
#                 D => input1
#             );
#         end Behavioral;
#     """
#     try:
#         out = infra.ise.synth("xc9536xl-5-VQ64", VHDL, ucf)
#         name = f"latch"
#         Path(name + ".jed").write_text(out)
#         bits = jed.parse(contents=out)[1]
#         db = { "bitstream_len": len(bits), "tags": { name: bits.nonzero()[0] } }
#         dump_html_for_tag(db, "latch")
#     except Exception as e:
#         print(e)

if __name__ == "__main__":
    output = "FB1_2"
    inputs = [f"FB1_{i}" for i in range(10,10+5)]
    ucf = f'NET "output" NOREDUCE="TRUE"; NET "output" LOC="{output}"; NET "clk" LOC="15";' " ".join(f'NET "input{i + 1}" LOC="{inputs[i]}";' for i in range(len(inputs)))
    VHDL = f"""
        library IEEE;
        use IEEE.STD_LOGIC_1164.ALL;
        library unisim;
        use UNISIM.vcomponents.ALL;

        entity passthrough is
            Port (clk : in STD_LOGIC; input1 : in STD_LOGIC; input2 : in STD_LOGIC; input3 : in STD_LOGIC; input4 : in STD_LOGIC; input5 : in STD_LOGIC; output: out STD_LOGIC);
        end passthrough;

        architecture Behavioral of passthrough is
            signal D : STD_LOGIC;
        begin
            output <= input1 xor ((input2 and input3) or (input4 and input5));
        end Behavioral;
    """
    try:
        out = infra.ise.synth("xc9536xl-5-VQ64", VHDL, ucf)
        name = f"latch"
        Path(name + ".jed").write_text(out)
        bits = jed.parse(contents=out)[1]
        db = { "bitstream_len": len(bits), "tags": { name: bits.nonzero()[0] } }
        dump_html_for_tag(db, "latch")
    except Exception as e:
        print(e)
