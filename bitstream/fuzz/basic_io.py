#!/usr/bin/env python3

from switch import bits_for_tag, dump_html_for_tag, fb_mc, print_bit
import database
from bitstream import bitstream
from json import load as load_json

def mc_config_bits(bits, mc):
    col = 6 + 8 * (mc % 9) + (mc % 18) // 9
    potential_bits = set(
        108 * i + col for i in range(108) if i not in [6, 7] and i < 50 or i > 76
    )
    potential_bits -= set([78 * 108 + 6, 78 * 108 + 54])
    return set(bit // 108 for bit in (bits & potential_bits))

def diff_tag(a, b, db, mc):
    a_bits = mc_config_bits(bits_for_tag(db, a), mc)
    b_bits = mc_config_bits(bits_for_tag(db, b), mc)
    return {a: a_bits - b_bits, b: b_bits - a_bits}

if __name__ == "__main__":
    with open("database/xc9536xl-5-VQ64.json") as f:
        db = load_json(f)
        db = database.bit_db_to_tag_db(db)

    tag_pairs = [
        ["init_0", "init_1"],
        ["fast_True", "fast_False"],
        ["slow_True", "slow_False"],
        ["pwr_mode_STD", "pwr_mode_LOW"],
        ["slew_SLOW", "slew_FAST"],
    ]

    for t in tag_pairs:
        for tag in t:
            dump_html_for_tag(db, tag)
        print(t, database.diff(db, *t), diff_tag(*t, db, 1))
