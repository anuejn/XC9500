from infra.bitstream import flat_bit_data, diff as diff_bitstream, decode_usercode
from colorhash import ColorHash

def gen_fb(fb_data, highlight, known):
    colors = {}

    ret = ""
    for key in set([color_key for title, color_key in known.values()]):
        color = ColorHash(key).hex
        colors[key] = color

        ret += '<div style="display: inline-block;">'
        ret += '<div style="padding-right: 20px;"><div style="display: inline-block; width: 17px; height: 17px; background-color: {};"></div> {}    </div>'.format(color, key)
        ret += '</div>'


    ret += '<div class="grid-container" style="cursor: default; user-select: none;">'

    for i in range(109):
        ret += '<div><span style="font-size: 5px; display: table">{}</span></div>'.format(i - 1 if i > 0 else " ")

    for i, bit in enumerate(fb_data):
        if i % 108 == 0:
            ret += '<div><span style="font-size: 5px; display: table">{}</span></div>'.format(i // 108)

        title = ""
        bit_color = None

        if i in highlight:
            title = "highlight"
            cls = "grid-item-highlight"
        elif bit:
            title = "set"
            cls = "grid-item-set"
        else:
            title = "unset"
            cls = "grid-item-unset"

            if i in known:
                title, color_key = known[i]
                bit_color = colors[color_key]

        if bit_color is not None:
            ret += '<div style="background-color: {};" class="{}">'.format(bit_color, cls)
        else:
            ret += '<div class="{}">'.format(cls)
        ret += '<span title="{}">{}</span>'.format(title, bit)
        ret += '</div>'

    ret += '</div>'

    return ret

# currently working of the assumption that for each function block the bitstream is a 108x108 square
def gen_html_view(filename, data, highlight, known, *, title=None):
    with open(filename, "w") as f:
        f.write("<!doctype html>")
        f.write("<head>")
        f.write("<style>")
        f.write("""
.grid-container {
  padding: 0;
  display: grid;
  align-items: center;
  grid-template-columns: repeat(109, 17px);
  grid-template-rows: repeat(109, 17px);
}
.grid-item-set {
  font-size: 10px;
  height: 100%;
  width: 100%;
  background-color: red;
  text-align: center;
}
.grid-item-unset {
  font-size: 10px;
  height: 100%;
  width: 100%;
  text-align: center;
  background-color: white;
}
.grid-item-highlight {
  font-size: 10px;
  height: 100%;
  width: 100%;
  text-align: center;
  background-color: blue;
}
        """)
        f.write("</style>")
        f.write("</head>")
        f.write("<body>")

        if title is not None:
            f.write("<h1>{}</h1>".format(title))

        for i, fb in enumerate(data):
            f.write("<h3> FB {} </h3>".format(i))
            f.write(gen_fb(fb, highlight[i], known[i]))
            f.write("<br /><br /><br />")

        f.write("</body>")


if False:
    outdir = "out/"
    base = outdir + "route_single_no_wysiwyg_1_2_to_1_1.jed"
    diff = outdir + "route_single_no_wysiwyg_1_3_to_1_1.jed"
    name = "base: {} [usercode: {}] diff: {} [usercode: {}]".format(base, decode_usercode(flat_bit_data(base, fb=None)), diff, decode_usercode(flat_bit_data(diff, fb=None)))
    data = flat_bit_data(base, fb=None)

    print(decode_usercode(data))

    diffs = []
    for fb in range(4):
        diff_position, a, b = diff_bitstream(base, diff, fb=fb)
        print("fb", fb, "diffs", diff_position, a, "->", b)
        diffs.append(diff_position)


    gen_html_view("test.html", data, diffs, [known, {}, {}, {}], title=name)

known = {}

offsets_pterm2 = [32, 72, 102, 33, 73, 103, 34, 74, 104, 35, 75, 105, 36, 76, 106, 37, 77, 107]
offsets_pterma = [0, 40, 78, 1, 41, 79, 2, 42, 80, 3, 43, 81, 4, 44, 82, 5, 45, 83]
offsets_ptermb = [8, 48, 84, 9, 49, 85, 10, 50, 86, 11, 51, 87, 12, 52, 88, 13, 53, 89]
offsets_ptermc = [16, 56, 90, 17, 57, 91, 18, 58, 92, 19, 59, 93, 20, 60, 94, 21, 61, 95]
offsets_ptermd = [24, 64, 96, 25, 65, 97, 26, 66, 98, 27, 67, 99, 28, 68, 100, 29, 69, 101]


pterm_names = ["2", "a", "b", "c", "d"]
offs = [offsets_pterm2, offsets_pterma, offsets_ptermb, offsets_ptermc, offsets_ptermd]

for i, offsets in enumerate(offs):
    for mc in range(18):
        mc += 1

        bits = []
        offset = offsets[mc - 1]
        for bit in range(108):
            bits.append(108 * 2 * bit + offset)
            bits.append(108 * (2 * bit + 1) + offset)

        for bit in bits:
            known[bit] = ("MC {} pterm {} and array input xx".format(mc, pterm_names[i]), "pterm_and_array")

usercode = []
for row in range(6, 8):
    for col in range(8):
        usercode.append(108 * row + 8 * col + 7)
        usercode.append(108 * row + 8 * col + 6)

for bit in usercode:
    known[bit] = ("usercode", "usercode")
