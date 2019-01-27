# Generate a list of all fuses for a given device

import re
import math
import pathlib

pathlib.Path("fusemaps").mkdir(parents=True, exist_ok=True)

for device in (l.strip() for l in open("devices.txt") if l.strip()):
    macrocell_cnt, io_cnt = [int(s) for s in re.match("XC95(\\d{2,3})XL-(\\d{2,3})", device).group(1, 2)]

    fuses = []

    function_blocks = range(macrocell_cnt // 18)
    ios = range(io_cnt)

    # generate the fast connect II fuses
    fc_bits = math.ceil(math.log2(io_cnt + macrocell_cnt))
    for fb in function_blocks:
        for i in range(54):
            for b in range(fc_bits):
                fuses.append("FC_FB%d_IN%d_BIT%d" % (fb, i, b))

    # generate the function block fuses
    for fb in function_blocks:
        for mc in range(18):
            # programmable and array
            for i in range(5):
                for f in range(54):
                    for inverted in ["P", "N"]:
                        fuses.append(
                            "FB%d_AND_MC%d_IN%d_FROM%d%s" % (fb, mc, i, f, inverted)
                        )
            # product term allocator
            for i in ["0", "1", "2", "3", "4", "5", "B", "A"]:
                for o in ["D", "S", "R", "C", "E", "B", "A"]:
                    fuses.append("FB%d_PTA_MC%d_IN%s_OUT%s" % (fb, mc, i, o))
            # macro cells
            for fuse in [
                "FFBYPASSP",
                "FFBYPASSN",
                "PTCLK",
                "G0CLK",
                "G1CLK",
                "G2CLK",
                "INVGSRP",
                "INVGSRN",
                "PTRESET",
                "GRESET",
                "PTSET",
                "GSET",
                "INVCLKP",
                "INVCLKN",
                "FFTYPE",
                "FFRSTVAL",
                "DXOR1",
                "DXOR0",
                "DXORIN",
            ]:
                fuses.append("FB%d_MC%d_%s" % (fb, mc, fuse))

    # generate io blocks
    for io in range(io_cnt):
        for fuse in [
            "SLEWRATE",
            "GROUND",
            "OEINVP",
            "OEINVN",
            "OE_0",
            "OE_1",
            "OE_PTOE",
            "OE_GOE0",
            "OE_GOE1",
        ]:
            fuses.append("IO%d_%s" % (io, fuse))

        if macrocell_cnt >= 144: 
            for fuse in ["OE_GOE2", "OE_GOE3"]:
                fuses.append("IO%d_%s" % (io, fuse))

    # write the file
    with open("fusemaps/%s.csv" % device, "w") as file:
        for fuse in fuses:
            file.write("%s\n" % fuse)
