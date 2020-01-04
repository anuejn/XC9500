from json import load as load_json
from database import bit_db_to_tag_db, diff

if __name__ == "__main__":
    with open("database/xc9536xl-5-VQ64.json") as f:
        db = load_json(f)

    db = bit_db_to_tag_db(db)

    for letter in range(4):
        for bit in range(8):
            print("letter {} bit {}: ".format(letter, bit), diff(db, "usercode", "usercode_letter_{}_bit_{}".format(letter, bit)))
