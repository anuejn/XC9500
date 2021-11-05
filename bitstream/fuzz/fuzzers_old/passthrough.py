def fuzz(device):
    def fb_mc(n):
        return f"FB{n // 18 + 1}_{n % 18 + 1}"

    for from_loc in range(288):
        for to_loc in range(1,3):
            VHDL = """
                library IEEE;
                use IEEE.STD_LOGIC_1164.ALL;
                library unisim;
                use UNISIM.vcomponents.ALL;

                entity passthrough is
                    Port ( output : out  STD_LOGIC; input: in STD_LOGIC);
                end passthrough;

                architecture Behavioral of passthrough is
                begin
                    output <= input;
                end Behavioral;
            """
            UCF = f"""
                NET "input" LOC="{fb_mc(from_loc)}"; NET "output"  LOC = "{fb_mc(to_loc)}";
            """

            tags = ["feedback_full", f"passthrough_from_{fb_mc(from_loc)}_to_{fb_mc(to_loc)}"]

            yield VHDL, UCF, tags
