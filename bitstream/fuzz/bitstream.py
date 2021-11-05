#!/usr/bin/env python3

import json
from pathlib import Path
from collections import defaultdict

# d is 1 (set)
# c is 4 (reset)

pterm_names = ["2", "a", "b", "c", "d"]
offsets_pterm2 = [32, 72, 102, 33, 73, 103, 34, 74, 104, 35, 75, 105, 36, 76, 106, 37, 77, 107]
offsets_pterma = [0, 40, 78, 1, 41, 79, 2, 42, 80, 3, 43, 81, 4, 44, 82, 5, 45, 83]
offsets_ptermb = [8, 48, 84, 9, 49, 85, 10, 50, 86, 11, 51, 87, 12, 52, 88, 13, 53, 89]
offsets_ptermc = [16, 56, 90, 17, 57, 91, 18, 58, 92, 19, 59, 93, 20, 60, 94, 21, 61, 95]
offsets_ptermd = [24, 64, 96, 25, 65, 97, 26, 66, 98, 27, 67, 99, 28, 68, 100, 29, 69, 101]
offs = [offsets_pterm2, offsets_pterma, offsets_ptermb, offsets_ptermc, offsets_ptermd]

export_database = {}
export_database["pterm_offsets"] = {
    "offset_1": offsets_ptermd,
    "offset_2": offsets_pterm2,
    "offset_4": offsets_ptermc,
    # these two are just guesses
    "offset_3": offsets_pterma,
    "offset_5": offsets_ptermb,
}
mc_cols = [6, 14, 22, 30, 38, 46, 54, 62, 70, 7, 15, 23, 31, 39, 47, 55, 63, 71]
export_database["macrocell_offsets"] = mc_cols

devices = {
    "36": {
        "fbs": 2
    },
    "72": {
        "fbs": 4
    },
    "144": {
        "fbs": 8
    },
    "288": {
        "fbs": 16
    },
}

bitstream = {
    device: {
        "mcs": {
            f"MC{mc + 1}": {
                "fb": mc // 18,
                "bits": {
                    108 * 108 * (mc // 18) + 108 * i + 6 + 8 * (mc % 9) + (mc % 18) // 9 for i in range(8, 50)
                },
                "product_terms": {
                    f"PT{pterm_names[pterm]}": {
                        "and_array": {
                            f"{i}_{'P' if i % 2 == 0 else 'N'}": 108 * 108 * (mc // 18) + 108 * i + offs[pterm][mc % 18]
                            for i in range(108)
                        }
                    }
                    for pterm in range(5)
                }
            }
            for mc in range(18 * devices[device]["fbs"])
        },
        "special": {
            "usercode": [
                108 * row + 8 * col + 6 + 1 - offs
                for row in range(6, 8)
                for col in range(8)
                for offs in range(2)
            ]
        }
    }
    for device in devices
}

imux = defaultdict(lambda: defaultdict(dict))

for device, data in json.loads(Path("imux.json").read_text()).items():
    imuxline_to_fb = {}
    for pad, config in data["pads"].items():
        mc = config["PinName"]
        if mc.startswith("MC"):
            fbmc = 18 * int(mc[2:4]) + int(mc[4:6])
            imuxline_to_fb[int(config["IMUXLine#"])] = fbmc

    for output, settings in data["imux"].items():
        for target, setting in settings.items():
            if target.startswith("F"):
                target = 10000 + int(target[1:])
            else:
                target = imuxline_to_fb[int(target)]


            imux[device][int(output)][setting] = target


export_database["imux"] = {}
export_database["global"] = {}
for device, configs in imux.items():
    bits = []
    device = ("XC" + device).lower()

    export_database["global"][device] = {
        "usercode": [
            108 * row + 8 * col + 6 + 1 - offs
            for row in range(6, 8)
            for col in range(8)
            for offs in range(2)
        ]
    }
    export_database["imux"][device] = [[{"type": "NC"} for _ in range(32)] for _ in range(54)]
    for output, settings in configs.items():
        for setting, target in settings.items():
            if target >= 10000:
                target -= 10000
                t = {
                    "type": "feedback",
                    "fb": target // 18,
                    "mc": target % 18
                }
            else:
                t = {
                    "type": "input",
                    "fb": target // 18,
                    "mc": target % 18
                }
            export_database["imux"][device][output][setting] = t


export_database["macrocell"] = {
    "slew_mode": {
        "bit": 44,
        "fast": "One",
        "slow": "Zero"
    },
    "ff_init": {
        "bit": 42,
        "one": "One",
        "zero": "Zero"
    },
    "ff_type": {
        "bit": 39,
        "t": "One",
        "d": "Zero"
    }
}


Path("../database.json").write_text(json.dumps(export_database))
