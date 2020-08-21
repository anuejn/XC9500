import itertools

def inverted(device):
    pins = ["FB{}_{}".format(fb, mc) for fb in range(1,3) for mc in range(1, 19)]
    for input_pins in  itertools.combinations(pins, 3):
        pins2 = ["FB{}_{}".format(fb, mc) for fb in range(1,3) for mc in range(1, 19)]
        for pin in input_pins:
            pins2.remove(pin)
        output_pin = pins2[0]

        VHDL = """
            library IEEE;
            use IEEE.STD_LOGIC_1164.ALL;

            entity passthrough is
                Port ( input_a : in  STD_LOGIC;
                       input_b : in  STD_LOGIC;
                       input_c : in  STD_LOGIC;
                       output : out  STD_LOGIC);
            end passthrough;

            architecture Behavioral of passthrough is
            begin
              output <= input_a and input_b and input_c;
            end Behavioral;
        """

        constrs = ['NET "input_a" LOC = "{}"'.format(input_pins[0])]
        constrs += ['NET "input_b" LOC = "{}"'.format(input_pins[1])]
        constrs += ['NET "input_c" LOC = "{}"'.format(input_pins[2])]
        constrs += ['NET "output" LOC = "{}"'.format(output_pin)]

        UCF = "; ".join(constrs) + ";"

        tags = ["passthrough_full_and_3_combinations", "passthrough_full_3_combinations_{}_and_{}_and_{}_to_{}".format(*input_pins, output_pin)]

        yield VHDL, UCF, tags
