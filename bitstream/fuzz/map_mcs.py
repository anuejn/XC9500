#!/usr/bin/env python3

from switch import bits_for_tag, dump_html_for_tag, fb_mc, print_bit
import database
from bitstream import bitstream
from json import load as load_json

if __name__ == "__main__":
    with open("database/xc9536xl-5-VQ64.json") as f:
        db = load_json(f)
        db = database.bit_db_to_tag_db(db)

    for mc in range(18):
        tag = f"constant_one_{fb_mc(mc)}"
        bits = bits_for_tag(db, tag)
        config = bitstream['36']['mcs']['MC' + str(mc + 1)]['bits']
        print(f"{fb_mc(mc)}: {print_bit(bits & config)}")
        dump_html_for_tag(db, tag)
    # print(database.diff(db, *t))

    # t = ["pwr_mode_STD", "pwr_mode_LOW"]
    # for tag in t:
    #     dump_html_for_tag(db, tag)
    # print(database.diff(db, *t))
