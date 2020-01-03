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
            NET "output"  LOC = "FB1_{}";
        """

        tags = ["constant_output_one", "FB1_{}".format(n)]

        yield VHDL, UCF.format(n), tags

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
            NET "output"  LOC = "FB1_{}";
        """

        tags = ["constant_output_zero", "FB1_{}".format(n)]

        yield VHDL, UCF.format(n), tags
