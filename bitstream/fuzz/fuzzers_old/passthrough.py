def inverted(device):
    for n in range(1, 19):
        VHDL = """
            library IEEE;
            use IEEE.STD_LOGIC_1164.ALL;

            entity passthrough is
                Port ( input : in  STD_LOGIC;
                       output : out  STD_LOGIC);
            end passthrough;

            architecture Behavioral of passthrough is
            begin
              output <= not input;

            end Behavioral;
        """
        UCF = """
            NET "input"  LOC = "FB2_01"; NET "output"  LOC = "FB1_{}";
        """

        tags = ["passthrough", "inverted", "FB1_{}".format(n)]

        yield VHDL, UCF.format(n), tags


def not_inverted(device):
    for n in range(1, 19):
        VHDL = """
            library IEEE;
            use IEEE.STD_LOGIC_1164.ALL;

            entity passthrough is
                Port ( input : in  STD_LOGIC;
                       output : out  STD_LOGIC);
            end passthrough;

            architecture Behavioral of passthrough is
            begin
              output <= input;

            end Behavioral;
        """
        UCF = """
            NET "input"  LOC = "FB2_01"; NET "output"  LOC = "FB1_{}";
        """

        tags = ["passthrough", "not_inverted", "FB1_{}".format(n)]

        yield VHDL, UCF.format(n), tags
