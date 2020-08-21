def constant_one(device):
    for fb in range(1, 3):
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

            tags = ["constant_output_one", "FB{}_{}".format(fb, n)]

            yield VHDL, UCF.format(fb, n), tags

def constant_zero(device):
    for fb in range(1, 3):
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

            tags = ["constant_output_zero", "FB{}_{}".format(fb, n)]

            yield VHDL, UCF.format(fb, n), tags
