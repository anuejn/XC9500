from bitstream.fuzz.ise import xst, ngdbuild, cpldfit, hprep6
from bitstream.fuzz.util import tmpfile, cat

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
        NET "input"  LOC = "FB1_08"; NET "output"  LOC = "FB2_10";
    """

    synth_result = xst(tmpfile(VHDL, suffix=".vhd"), "passthrough")
    ndg_file = ngdbuild(ngc_file=synth_result, device=DEVICE, ucf_file=tmpfile(UCF, suffix=".ucf"))
    fit_result = cpldfit(ndg_file=ndg_file, device=DEVICE)
    jedec = hprep6(vm6_file=fit_result, label="test")
    jedec_content = cat(jedec).decode("utf-8")

    print(jedec_content)
