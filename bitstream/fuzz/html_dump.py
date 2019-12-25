from bitstream import flat_bit_data

def gen_fb(fb_data):
    ret = ""
    ret += '<div class="grid-container">'

    for bit in fb_data:
        if bit:
            cls = "grid-item-set"
        else:
            cls = "grid-item-unset"

        ret += '<div class="{}">'.format(cls)
        ret += str(bit)
        ret += '</div>'

    ret += '</div>'

    return ret

# currently working of the assumption that for each function block the bitstream is a 108x108 square
def gen_html_view(filename, data, highlight):
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
        """)
        f.write("</style>")
        f.write("</head>")
        f.write("<body>")

        for fb in data:
            f.write(gen_fb(fb))
            f.write("<br /><br /><br />")

        f.write("</body>")


data = flat_bit_data("out/1_0.jed", fb=None)
gen_html_view("test.html", data, None)
