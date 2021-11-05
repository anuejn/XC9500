#!/usr/bin/env python3

from collections import defaultdict
import json
from pathlib import Path

with open("xc9500xl.chp") as f:
    chips = defaultdict(dict)
    current_chip = None
    in_io = False
    in_imux = False
    in_package_mapping = False
    for l in f:
        if l.startswith('CHIP'):
            _, codename, part_num = l.split()
            if codename != "EPLD":
                current_chip = part_num
                chips[part_num]["codename"] = codename
            else:
                in_package_mapping = True
        elif in_package_mapping:
            if l.startswith('END'):
                in_package_mapping = False
            else:
                name, base = l.split()
                chip = base[:base.find("XL") + 2]
                if chip not in chips:
                    chips[chip]["package_mapping"] = {}
                chips[chip]["package_mapping"][name] = base


        elif l.startswith('FB'):
            chips[current_chip]["num_fb"] = int(l.split()[1])
        elif l.startswith('PadNo'):
            io_header = l.split()
            chips[current_chip]["pads"] = defaultdict(dict)
            in_io = True
        elif in_io:
            if l.startswith('END'):
                in_io = False
            else:
                data = l.split()
                if data[0] != ".":
                    chips[current_chip]["pads"][int(data[0])] = { col: value for col, value in zip(io_header, data) }
        elif l.startswith('OUT#'):
            in_imux = True
            imux_header = [int(e[1:]) for e in l.split()[1:]]
            chips[current_chip]["imux"] = defaultdict(dict)
        elif in_imux:
            if l.startswith('IMUX END'):
                in_imux = False
            else:
                out, *configs = l.split()
                chips[current_chip]["imux"][out] = {config: value for config, value in zip(configs, imux_header)}

    Path("imux.json").write_text(json.dumps(chips, indent=4))
