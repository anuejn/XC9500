#!/usr/bin/env python3

def basic(device):
    # these should be bonded on all relevant devices
    output = "FB1_2"
    input = "FB1_3"

    def base(b, u, *tags):

        VHDL = f"""
            library IEEE;
            use IEEE.STD_LOGIC_1164.ALL;
            library unisim;
            use UNISIM.vcomponents.ALL;

            entity passthrough is
                Port ( output : out  STD_LOGIC; input : in STD_LOGIC);
            end passthrough;

            architecture Behavioral of passthrough is
            begin
                {b}
            end Behavioral;
        """
        UCF = f"""
            NET "output"  LOC = "{output}"; NET "input"  LOC = "{input}"; {u}

        """
        if "FDCE_inst" in VHDL:
            UCF += 'INST "FDCE_inst" KEEP=TRUE; INST "FDCE_inst" LOC="{output}";'
        yield VHDL, UCF, tags

    for init in [0, 1]:
        yield from base(
            f"""
                FDCE_inst: FDCE
                generic map (
                    INIT => '{init}'
                )
                port map (
                Q => output,
                C => '0',
                CE => '0',
                CLR => '0',
                D => input
                );
            """,
            "",
            f"init_{init}"
        )

    for fast in [True, False]:
        yield from base(
            f"""
            output <= input;
            """,
            f'NET "output" FAST; ' if fast else "",
            f"fast_{fast}"
        )

    for slow in [True, False]:
        yield from base(
            f"""
            output <= input;
            """,
            f'NET "output" SLOW; ' if slow else "",
            f"slow_{slow}"
        )

    for mode in ["STD", "LOW"]:
        yield from base(
            f"""
            output <= input;
            """,
            f'NET "output" PWR_MODE={mode};',
            f"pwr_mode_{mode}"
        )

    for slew in ["SLOW", "FAST"]:
        yield from base(
            f"""
            output <= input;
            """,
            f'NET "output" SLEW={slew};',
            f"slew_{slew}"
        )

def constant_one(device):
    for n in range(1, 19):
        VHDL = """
            library IEEE;
            use IEEE.STD_LOGIC_1164.ALL;

            entity passthrough is
                Port ( output : out  STD_LOGIC);
            end passthrough;

            architecture Behavioral of passthrough is
            begin
                output <= '1';
            end Behavioral;
        """
        UCF = """
            NET "output"  LOC = "FB{}_{}";
        """

        tags = ["constant_output_one", "constant_one_FB{}_{}".format(1, n)]

        yield VHDL, UCF.format(1, n), tags

def constant_zero(device):
    for n in range(1, 19):
        VHDL = """
            library IEEE;
            use IEEE.STD_LOGIC_1164.ALL;

            entity passthrough is
                Port ( output : out  STD_LOGIC);
            end passthrough;

            architecture Behavioral of passthrough is
            begin
                output <= '0';
            end Behavioral;
        """
        UCF = """
            NET "output"  LOC = "FB{}_{}";
        """

        tags = ["constant_output_one", "constant_one_FB{}_{}".format(1, n)]

        yield VHDL, UCF.format(1, n), tags
