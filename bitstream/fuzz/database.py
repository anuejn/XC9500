from collections import defaultdict

def bit_db_to_tag_db(db):
    size = db["bitstream_len"]

    tags = defaultdict(set)

    for bit, bit_tags in db["bits"].items():
        for tag in bit_tags:
            tags[tag].add(bit)

    return {"bitstream_len": size, "tags": tags }


def diff(db, tag_a, tag_b):
    db = db["tags"]

    bits_a = db[tag_a]
    bits_b = db[tag_b]

    common = bits_a.intersection(bits_b)

    only_in_a = bits_a.difference(common)
    only_in_b = bits_b.difference(common)

    return only_in_a, only_in_b
