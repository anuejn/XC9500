def usercode(device):
    VHDL = """
        library IEEE;
        use IEEE.STD_LOGIC_1164.ALL;

        entity empty is
        end empty;

        architecture Behavioral of empty is begin
        end Behavioral;
    """
    UCF = ""
    tags = ["usercode"]

    yield VHDL, UCF, tags, {"usercode": "".join([chr(c) for c in [0x80, 0x80, 0x80, 0x80]])}

    for letter in range(4):
        for bit in range(8):
            tags = ["usercode_letter_{}_bit_{}".format(letter, bit)]

            letters = [0x80, 0x80, 0x80, 0x80]
            # letters[letter] = (~(1 << bit)) & 0xff
            letters[letter] = (1 << bit)

            print("".join([chr(c) for c in letters]))

            yield VHDL, UCF, tags, {"usercode": "".join([chr(c) for c in letters])}
