def inverted(device):
    for a in range(1, 3):
        for b in range(1, 3):
            for n in range(1, 19):
                for m in range(1, 19):
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
                        NET "input"  LOC = "FB{}_{}"; NET "output"  LOC = "FB{}_{}";
                    """

                    tags = ["passthrough_full", "passthrough_full_inverted", "passthrough_full_from_FB{}_{}_to_FB{}_{}".format(a,n,b,m)]

                    yield VHDL, UCF.format(a,n,b,m), tags


def not_inverted(device):
    for a in range(1, 3):
        for b in range(1, 3):
            for n in range(1, 19):
                for m in range(1, 19):
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
                        NET "input"  LOC = "FB{}_{}"; NET "output"  LOC = "FB{}_{}";
                    """

                    tags = ["passthrough_full", "passthrough_full_not_inverted", "passthrough_full_from_FB{}_{}_to_FB{}_{}".format(a,n,b,m)]

                    yield VHDL, UCF.format(a,n,b,m), tags

