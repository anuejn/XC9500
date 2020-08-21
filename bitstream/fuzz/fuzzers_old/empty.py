def empty(device):
    VHDL = """
        library IEEE;
        use IEEE.STD_LOGIC_1164.ALL;

        entity empty is
        end empty;

        architecture Behavioral of empty is begin
        end Behavioral;
    """
    UCF = ""

    tags = ["empty"]

    yield VHDL, UCF, tags
