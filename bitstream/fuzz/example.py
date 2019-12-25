from multiprocessing import Pool
import ise


def mapper(n):
    return ise.synth(DEVICE, VHDL, UCF.format(n))


if __name__ == "__main__":
    DEVICE="xc9536xl-5-VQ64"
    VHDL="""
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
    UCF="""
        NET "input"  LOC = "FB1_08"; NET "output"  LOC = "FB2_{}";
    """

    with Pool(18) as p:
        jedecs = p.map(mapper, range(1, 19))

    print(jedecs)
