def inverted(device):
    for t_fb in  range(1, 3):
        for t_mc in range(1, 2):
            for a in range(1, 3):
                for b in range(1, 3):
                    for n in range(1, 19):
                        for m in range(1, 19):
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
                                      output <= input_a and input_b;

                                    end Behavioral;
                                """
                                UCF = """
                                    NET "input_a"  LOC = "FB{}_{}"; NET "input_b"  LOC = "FB{}_{}"; NET "output"  LOC = "FB{}_{}";
                                """

                                tags = ["passthrough_full_and", "passthrough_full_and_from_FB{}_{}_and_FB{}_{}_to_FB{}_{}".format(a,n,b,m,t_fb,t_mc)]

                                yield VHDL, UCF.format(a,n,b,m,t_fb,t_mc), tags
