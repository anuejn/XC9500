def inverted(device):
    for from_mc in  range(1, 19):
        if from_mc == 1:
            to_mc = 2
        else:
            to_mc = 1

        VHDL = """
            library IEEE;
            use IEEE.STD_LOGIC_1164.ALL;

            entity passthrough is
                Port ( input_a : in  STD_LOGIC;
                       input_1 : in  STD_LOGIC;
                       input_2 : in  STD_LOGIC;
                       input_3 : in  STD_LOGIC;
                       input_4 : in  STD_LOGIC;
                       input_5 : in  STD_LOGIC;
                       input_6 : in  STD_LOGIC;
                       input_7 : in  STD_LOGIC;
                       input_8 : in  STD_LOGIC;
                       input_9 : in  STD_LOGIC;
                       input_10 : in  STD_LOGIC;
                       input_11 : in  STD_LOGIC;
                       input_12 : in  STD_LOGIC;
                       input_13 : in  STD_LOGIC;
                       input_14 : in  STD_LOGIC;
                       input_15 : in  STD_LOGIC;
                       input_16 : in  STD_LOGIC;
                       input_17 : in  STD_LOGIC;
                       input_18 : in  STD_LOGIC;
                       output : out  STD_LOGIC);
            end passthrough;

            architecture Behavioral of passthrough is
            begin
              output <= input_a and input_1 and input_2 and  input_3 and  input_4 and  input_5 and  input_6 and  input_7 and  input_8 and  input_9 and  input_10 and input_11 and input_12 and  input_13 and  input_14 and  input_15 and  input_16 and  input_17 and  input_18;
            end Behavioral;
        """

        constrs = ['NET "input_{}" LOC = "FB2_{}"'.format(i, i) for i in range(1, 19)]
        constrs += ['NET "input_a" LOC = "FB1_{}"'.format(from_mc)]
        constrs += ['NET "output" LOC = "FB1_{}"'.format(to_mc)]

        UCF = "; ".join(constrs) + ";"

        tags = ["passthrough_full_and_many", "passthrough_full_and_many_from_FB1_{}_and_FB2_to_FB1_{}".format(from_mc, to_mc)]

        yield VHDL, UCF, tags
