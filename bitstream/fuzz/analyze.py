from json import load as load_json
import database
from math import ceil
import itertools


def format_space(space):
    if space > 100:
        return ">>"
    return ceil((space - 1) / 10) * "."


def with_bg(str, color):
    if color == "red":
        color = "\u001b[41m"
    elif color == "green":
        color = "\u001b[42m"
    elif color == "none":
        return str
    else:
        assert False, "the color is unknown"
    return "\u001b[30m{color}{str}\33[0m".format(color=color, str=str)


def format_diff(diff):
    removals = [("red", x) for x in diff[0]]
    additions = [("green", x) for x in diff[1]]
    all = sorted([*removals, *additions], key=lambda x: x[1])
    with_spaces = list(itertools.chain.from_iterable([
        [this,
         (
             "none",
             format_space(int(next[1]) - int(this[1]))
         )
         ] for this, next in zip(all, [*all[1:], (0, 0)])
    ]))
    colored = [with_bg(x[1], x[0]) for x in with_spaces]
    return " ".join(colored)


if __name__ == "__main__":
    with open("database/xc9536xl-5-VQ64.json") as f:
        db = load_json(f)

    db = database.bit_db_to_tag_db(db)

    for letter in range(4):
        for bit in range(8):
            diff = database.diff(db, "usercode", "usercode_letter_{}_bit_{}".format(letter, bit))
            print("letter {} bit {}: ".format(letter, bit), format_diff(diff))
