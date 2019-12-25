from bitstream import flat_bit_data, diff
from colorhash import ColorHash

def gen_fb(fb_data, highlight, known):
    colors = {}

    ret = ""
    for key in known.keys():
        color = ColorHash(key).hex
        colors[key] = color

        ret += '<div style="display: inline-block;">'
        ret += '<div style="padding-right: 20px;"><div style="display: inline-block; width: 17px; height: 17px; background-color: {};"></div> {}    </div>'.format(color, key)
        ret += '</div>'


    ret += '<div class="grid-container" style="cursor: default; user-select: none;">'

    for i, bit in enumerate(fb_data):
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

            for key, bits in known.items():
                if i in bits:
                    title = key
                    bit_color = colors[key]

        if bit_color is not None:
            ret += '<div style="background-color: {};" class="{}">'.format(bit_color, cls)
        else:
            ret += '<div class="{}">'.format(cls)
        ret += '<span title="{}">{}</span>'.format(title, bit)
        ret += '</div>'

    ret += '</div>'

    return ret

# currently working of the assumption that for each function block the bitstream is a 108x108 square
def gen_html_view(filename, data, highlight, known):
    with open(filename, "w") as f:
        f.write("<!doctype html>")
        f.write("<head>")
        f.write("<style>")
        f.write("""
.grid-container {
  padding: 0;
  display: grid;
  align-items: center;
  grid-template-columns: repeat(108, 17px);
  grid-template-rows: repeat(108, 17px);
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

        for i, fb in enumerate(data):
            f.write("<h3> FB {} </h3>".format(i))
            f.write(gen_fb(fb, highlight[i], known[i]))
            f.write("<br /><br /><br />")

        f.write("</body>")


data = flat_bit_data("out/1_0_xor.jed", fb=None)
diff_position, a, b = diff("out/1_0_xor.jed", "out/1_1_xor.jed")

known = {}

offsets = [0, 40, 78, 1, 41, 79, 2, 42, 80, 3, 43, 81, 4, 44, 82, 5, 45, 83]

for mc in range(18):
    mc += 1

    bits = []
    offset = offsets[mc - 1]
    for bit in range(108):
        bits.append(108 * 2 * bit + offset)
        bits.append(108 * (2 * bit + 1) + offset)

    known["MC {} input 0?".format(mc)] = bits

gen_html_view("test.html", data, [diff_position, [], [], []], [known, {}, {}, {}])
