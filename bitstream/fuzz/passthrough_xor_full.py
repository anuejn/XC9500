def inverted(device):
    for t_fb in  range(1, 3):
        for t_mc in range(1, 3):
            for a in range(1, 3):
                for b in range(1, 3):
                    for n in range(1, 19):
                        for m in range(1, 19):
                            for k in range(0, 4):
                                VHDL = """
                                    library IEEE;
                                    use IEEE.STD_LOGIC_1164.ALL;

                                    entity passthrough is
                                        Port ( input_a : in  STD_LOGIC;
                                               input_b : in  STD_LOGIC;
                                               output : out  STD_LOGIC);
                                    end passthrough;

                                    architecture Behavioral of passthrough is
                                    begin
                                      output <= {} input_a xor {} input_b;

                                    end Behavioral;
                                """
                                UCF = """
                                    NET "input_a"  LOC = "FB{}_{}"; NET "input_b"  LOC = "FB{}_{}"; NET "output"  LOC = "FB{}_{}";
                                """

                                not_combis = [["", ""], ["not", ""], ["", "not"], ["not", "not"]]

                                tags = ["passthrough_full_xor", "passthrough_full_{}_{}".format(*not_combis[k]), "passthrough_full_xor_from_FB{}_{}_xor_FB{}_{}_to_FB{}_{}".format(a,n,b,m,t_fb,t_mc)]

                                yield VHDL.format(*not_combis[k]), UCF.format(a,n,b,m,t_fb,t_mc), tags
