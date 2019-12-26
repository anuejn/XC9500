def not_inverted(device):
    for n in range(18):
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
            NET "input"  LOC = "FB1_08"; NET "output"  LOC = "FB2_{}";
        """

        tags = ["passthrough", "FB2_{}".format(n), "inverted"]

        yield VHDL, UCF.format(n), tags


def inverted(device):
    for n in range(18):
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
            NET "input"  LOC = "FB1_08"; NET "output"  LOC = "FB2_{}";
        """

        tags = ["passthrough", "inverted", "FB2_{}".format(n)]

        yield VHDL, UCF.format(n), tags
