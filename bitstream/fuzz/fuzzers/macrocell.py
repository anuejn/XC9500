#!/usr/bin/env python3

# def basic(device):
#     # these should be bonded on all relevant devices
#     output = "FB1_2"
#     aux_output = "FB1_5"
#     input = "FB1_3"

#     def base(b, u, *tags, i = ""):

#         VHDL = f"""
#             library IEEE;
#             use IEEE.STD_LOGIC_1164.ALL;
#             library unisim;
#             use UNISIM.vcomponents.ALL;

#             entity passthrough is
#                 Port ( {i} io : inout  STD_LOGIC; output : out STD_LOGIC );
#             end passthrough;

#             architecture Behavioral of passthrough is
#             begin
#                 {b}
#             end Behavioral;
#         """
#         UCF = f"""
#             NET "io"  LOC = "{output}"; NET "output" LOC="{aux_output}"; {u}

#         """
#         if "IOBUFE_inst" in VHDL:
#             UCF += f'INST "IOBUFE_inst" KEEP=TRUE; INST "IOBUFE_inst" LOC="{output}";'
#         yield VHDL, UCF, tags

#     for e in [0, 1]:
#         yield from base(
#             f"""
#             IOBUFE_inst : IOBUFE
#             port map (
#                 O => output,
#                 IO => io,
#                 I => '0',
#                 E => '{e}'
#             );
#             """,
#             "",
#             f"iobufe_e_{e}"
#         )

#     yield from base(
#         f"""
#         IOBUFE_inst : IOBUFE
#         port map (
#             O => output,
#             IO => io,
#             I => '0',
#             E => input
#         );
#         """,
#         f'NET "input" LOC="{input}";',
#         f"iobufe_e_io",
#         i = "input : in STD_LOGIC; "
#     )

# def gclk(device):
#     # these should be bonded on all relevant devices
#     output = "FB1_2"
#     aux_input = "FB1_5"
#     aux_input2 = "FB1_6"
#     input = "FB1_3"

#     def base(b, u, *tags, i = ""):
#         VHDL = f"""
#             library IEEE;
#             use IEEE.STD_LOGIC_1164.ALL;
#             library unisim;
#             use UNISIM.vcomponents.ALL;

#             entity passthrough is
#                 Port ( clk : in STD_LOGIC; input : in STD_LOGIC; output : out STD_LOGIC );
#             end passthrough;

#             architecture Behavioral of passthrough is
#             begin
#                 inst: FDCE
#                 generic map (
#                     INIT => '0'
#                 )
#                 port map (
#                     Q => output,
#                     C => {b} clk,
#                     CE => '0',
#                     CLR => '0',
#                     D => input
#                 );
#             end Behavioral;
#         """
#         UCF = f"""
#             NET "output"  LOC = "{output}"; NET "input" LOC="{input}"; {u}
#         """
#         if "inst" in VHDL:
#             UCF += f'INST "inst" KEEP=TRUE; INST "inst" LOC="{output}";'
#         yield VHDL, UCF, tags

#     for gck, pin in [(1, "M2"), (2, "M3"), (3, "P5")]:
#         for n in ["not", ""] if gck == 1 else [""]:
#             yield from base(
#                 f"{n} ",
#                 f'NET "clk" LOC="{pin}";',
#                 f"clk_gck{'_not' if len(n) > 0 else ''}_{gck}"
#             )

#     yield from base(
#         "",
#         f'NET "clk" LOC="{aux_input}";',
#         f"clk_gck_pterm"
#     )

# def g_set(device):
#     # these should be bonded on all relevant devices
#     output = "FB1_2"
#     aux_input = "FB1_5"
#     aux_input2 = "FB1_6"
#     input = "FB1_3"

#     def base(b, u, *tags, i = ""):
#         VHDL = f"""
#             library IEEE;
#             use IEEE.STD_LOGIC_1164.ALL;
#             library unisim;
#             use UNISIM.vcomponents.ALL;

#             entity passthrough is
#                 Port ( input : in STD_LOGIC; output : out STD_LOGIC );
#             end passthrough;

#             architecture Behavioral of passthrough is
#             begin
#                 inst: FDCPE
#                 generic map (
#                     INIT => '0'
#                 )
#                 port map (
#                     Q => output,
#                     C => '0',
#                     CE => '0',
#                     CLR => '0',
#                     PRE => {b} input,
#                     D => '0'
#                 );
#             end Behavioral;
#         """
#         UCF = f"""
#             NET "output"  LOC = "{output}"; {u}
#         """
#         # if "inst" in VHDL:
#         #     UCF += f'INST "inst" KEEP=TRUE; INST "inst" LOC="{output}";'
#         yield VHDL, UCF, tags

#     for gsr, pin in [(1, "C4")]:
#         for n in ["not", ""]:
#             yield from base(
#                 f"{n} ",
#                 f'NET "input" LOC="{pin}";',
#                 f"ff_set{'_not' if len(n) > 0 else ''}_{gsr}"
#             )

#     yield from base(
#         "",
#         f'NET "input" LOC="{input}";',
#         f"ff_set_pterm"
#     )


# def g_reset(device):
#     # these should be bonded on all relevant devices
#     output = "FB1_2"
#     aux_input = "FB1_5"
#     aux_input2 = "FB1_6"
#     input = "FB1_3"

#     def base(b, u, *tags, i = ""):
#        VHDL = f"""
#             library IEEE;
#             use IEEE.STD_LOGIC_1164.ALL;
#             library unisim;
#             use UNISIM.vcomponents.ALL;

#             entity passthrough is
#                 Port ( input : in STD_LOGIC; output : out STD_LOGIC );
#             end passthrough;

#             architecture Behavioral of passthrough is
#             begin
#                 inst: FDCPE
#                 generic map (
#                     INIT => '0'
#                 )
#                 port map (
#                     Q => output,
#                     C => '0',
#                     CE => '0',
#                     CLR => {b} input,
#                     PRE => '0',
#                     D => '0'
#                 );
#             end Behavioral;
#         """
#         UCF = f"""
#             NET "output"  LOC = "{output}"; {u}
#         """
#         # if "inst" in VHDL:
#         #     UCF += f'INST "inst" KEEP=TRUE; INST "inst" LOC="{output}";'
#         yield VHDL, UCF, tags

#     for gsr, pin in [(1, "C4")]:
#         for n in ["not", ""]:
#             yield from base(
#                 f"{n} ",
#                 f'NET "input" LOC="{pin}";',
#                 f"ff_reset{'_not' if len(n) > 0 else ''}_{gsr}"
#             )

#     yield from base(
#         "",
#         f'NET "input" LOC="{input}";',
#         f"ff_reset_pterm"
#     )

# def ff_type(device):
#     output = "FB1_2"
#     # input = "FB1_3"
#     input = "M2"
#     aux_input = "FB1_5"
#     aux_input2 = "FB1_6"
#     aux_input3 = "FB1_8"
#     def base(b, u, *tags, i = ""):
#         VHDL = f"""
#             library IEEE;
#             use IEEE.STD_LOGIC_1164.ALL;
#             library unisim;
#             use UNISIM.vcomponents.ALL;

#             entity passthrough is
#                 Port ( input : in STD_LOGIC; clk : in STD_LOGIC; output : out STD_LOGIC );
#             end passthrough;

#             architecture Behavioral of passthrough is
#             begin
#                 {b}
#             end Behavioral;
#         """
#         UCF = f"""
#             NET "output" LOC="{output}"; NET "clk" LOC="{input}"; NET "input" LOC="{aux_input}";
# #            NET "input2" LOC="{aux_input2}";
# #            NET "input2" LOC="{aux_input3}";
# #            INST "inst" REG="DFF";
# #            INST "inst" KEEP=TRUE; INST "inst" LOC="{output}";
#         """
#         yield VHDL, UCF, tags
#     yield from base(
#         """
#         inst: FDCPE
#         -- generic map (
#         --     INIT => '1'
#         -- )
#         port map (
#             Q => output,
#             C => '0',
#             CE => '1',
#             CLR => '0',
#             PRE => '0',
#             D => input
#         );
#         """,
#         '',
#         f"ff_type_d"
#     )

#     yield from base(
#         """
#         inst: FTCP
#         -- generic map (
#         --     INIT => '1'
#         -- )
#         port map (
#             Q => output,
#             C => '0',
#             CLR => '0',
#             PRE => '0',
#             T => input
#         );
#         """,
#         '',
#         f"ff_type_t"
#     )

#     yield from base(
#         """
#         inst: LDCP
#         -- generic map (
#         --     INIT => '0'
#         -- )
#         port map (
#             Q => output,
#             G => '0',
#             CLR => '0',
#             PRE => '0',
#             D => input
#         );
#         """,
#         '',
#         f"ff_type_ld"
#     )

#     yield from base(
#         """
#         output <= input;
#         """,
#         '',
#         f"passthrough"
#     )

# def obuft(device):
#     # these should be bonded on all relevant devices
#     output = "FB1_2"
#     input = "FB1_3"

#     def base(b, u, *tags, i = ""):

#         VHDL = f"""
#             library IEEE;
#             use IEEE.STD_LOGIC_1164.ALL;
#             library unisim;
#             use UNISIM.vcomponents.ALL;

#             entity passthrough is
#                 Port ( {i} output : out  STD_LOGIC );
#             end passthrough;

#             architecture Behavioral of passthrough is
#             begin
#                 {b}
#             end Behavioral;
#         """
#         UCF = f"""
#             NET "output"  LOC = "{output}"; {u}

#         """
#         if "inst" in VHDL:
#             UCF += f'INST "inst" KEEP=TRUE; INST "inst" LOC="{output}";'
#         yield VHDL, UCF, tags

#     for e in [0, 1]:
#         yield from base(
#             f"""
#             inst : OBUFT
#             port map (
#                 O => output,
#                 I => '0',
#                 T => '{e}'
#             );
#             """,
#             "",
#             f"obuft_t_{e}"
#         )

#     for n in ["not ", ""]:
#         yield from base(
#             f"""
#             inst : OBUFT
#             port map (
#                 O => output,
#                 I => '0',
#                 T => {n} input
#             );
#             """,
#             f'NET "input" LOC="{input}";',
#             f"obuft_t{'_not' if len(n) > 0 else ''}_pterm_io",
#             i = "input : in STD_LOGIC; "
#         )

#         # for gts, pin in [(1, 5), (2, 2)]:
#         for gts, pin in [(1, "D4"), (2, "E5"), (3, "D3"), (4, "E3")]:
#             yield from base(
#                 f"""
#                 inst : OBUFT
#                 port map (
#                     O => output,
#                     I => '0',
#                     T => {n} gts
#                 );
#                 """,
#                 f'NET "gts" LOC="{pin}";',
#                 f"obuft_t{'_not' if len(n) > 0 else ''}_gts_{gts}",
#                 i = "gts : in STD_LOGIC; "
#             )




"""
['init_0', 'init_1'] (set(), {'9094'}) {'init_0': set(), 'init_1': {42}}
['fast_True', 'fast_False'] (set(), set()) {'fast_True': set(), 'fast_False': set()}
['slow_True', 'slow_False'] (set(), {'9526'}) {'slow_True': set(), 'slow_False': {44}}
['pwr_mode_STD', 'pwr_mode_LOW'] ({'9742', '5638'}, set()) {'pwr_mode_STD': {26, 45}, 'pwr_mode_LOW': set()}
['slew_SLOW', 'slew_FAST'] (set(), {'9526'}) {'slew_SLOW': set(), 'slew_FAST': {44}}
"""
