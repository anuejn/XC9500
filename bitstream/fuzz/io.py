#!/usr/bin/env python3

from switch import bits_for_tag, dump_html_for_tag, fb_mc, parse_switch, print_bit
import database
from bitstream import bitstream
from json import load as load_json
from basic_io import diff_tag
import itertools

if __name__ == "__main__":
    with open("database/xc95288xl-6-FG256.json") as f:
        db = load_json(f)
        db = database.bit_db_to_tag_db(db)

    tags = db['tags'].keys()
    # tags = ["iobufe_e_0", "iobufe_e_1", "iobufe_io", "obuft_t_0", "obuft_t_1",
    #         "obuft_t_pterm_io", "obuft_t_not_pterm_io",
    #         "obuft_t_gts_1", "obuft_t_not_gts_1",
    #         "obuft_t_gts_2", "obuft_t_not_gts_2",
    #         "obuft_t_gts_3", "obuft_t_not_gts_3",
    #         "obuft_t_gts_4", "obuft_t_not_gts_4",
    #         "clk_gck_pterm", "clk_gck_not_1", "clk_gck_1", "clk_gck_2", "clk_gck_3",

    #         ]
    tag_pairs = itertools.combinations(tags, 2)

    for tag in tags:
        print(tag, parse_switch(bits_for_tag(db, tag), 0, '288'))
        dump_html_for_tag(db, tag)


    for t in tag_pairs:
        print(t, database.diff(db, *t), diff_tag(*t, db, 1))
