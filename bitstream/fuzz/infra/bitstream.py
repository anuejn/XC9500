from infra.jed import parse as parse_jed
import subprocess
import numpy as np


def parse_devicename(name):
    data = {}

    device, speedgrade, package = name.split("-")

    data["device"] = device
    data["speedgrad"] = speedgrade
    data["package"] = package

    submodel = int(device[4:-2], 10)
    function_blocks = submodel / 18

    if int(function_blocks) != function_blocks:
        print("unknown device submodel {} from devicename {}".format(submodel, name))
    else:
        data["function_blocks"] = int(function_blocks)

    return data


def devicename_from_notes(notes):
    for note in notes:
        if note.startswith("DEVICE"):
            return note[7:]


# we currently assume that the bits are organized in columns with one column per function block
# the columns have a repeating pattern of 9 times 8 bits and then 6 times 6 bits
# there are always 108 of these blocks
# this means in total there are 108 * (9 * 8 + 6 * 6) = 11664 bits per column / function block
def split_into_functionblocks(data, function_blocks, flat=False):
    bits_in_first_pattern = function_blocks * 9 * 8
    bits_in_second_pattern = function_blocks * 6 * 6

    bits_per_pattern = bits_in_first_pattern + bits_in_second_pattern

    blocks = data.reshape((108, bits_per_pattern))

    fb_data = [[] for _ in range(function_blocks)]

    for block in blocks:
        first_pattern = block[:bits_in_first_pattern]
        second_pattern = block[bits_in_first_pattern:]

        first_pattern = first_pattern.reshape((9, function_blocks, 8))
        second_pattern = second_pattern.reshape((6, function_blocks, 6))

        for fb in range(function_blocks):
            d = first_pattern[:, fb, :]

            if flat:
                d = np.ravel(d)

            fb_data[fb].append(d)

        for fb in range(function_blocks):
            d = second_pattern[:, fb, :]

            if flat:
                d = np.ravel(d)

            fb_data[fb].append(d)

    return fb_data


def flat_bit_data(jed, fb=0):
    config, data = parse_jed(jed)

    device = parse_devicename(devicename_from_notes(config["notes"]))
    fb_data = split_into_functionblocks(data, device["function_blocks"], flat=True)

    if fb is not None:
        bit_data = np.concatenate(fb_data[fb])
    else:
        bit_data = []
        for fb in range(device["function_blocks"]):
            bit_data.append(np.concatenate(fb_data[fb]))

    return bit_data


def diff(a, b, fb=0):
    a_data = flat_bit_data(a, fb=fb)
    b_data = flat_bit_data(b, fb=fb)

    where = np.where(a_data != b_data)

    return (where[0], a_data[where], b_data[where])


def fuzz_and_array(base):
    for mc in range(18):
        mc = mc + 1
        for i in range(54):
            i = i + 1

            diff_position, a, b = diff(base + str(mc) + "_0.jed", base + str(mc) + "_{}.jed".format(i))

            m, n = diff_position

            print("mc {: 3} base vs inv {: 3} differ at".format(mc, i), "[{: 4} * 108 + {: 3}, {: 4} * 108 + {: 3}]".format(m // 108, m % 108, n // 108, n % 108), "values changed from", a, "->", b)

def fuzz_and_array_xor(base):
    for mc in range(18):
        mc = mc + 1
        for i in range(45, 47):
            i = i + 1

            diff_position, a, b = diff(base + str(mc) + "_0_xor.jed", base + str(mc) + "_{}_xor.jed".format(i))

            # print(mc, i)
            # print(diff_position)

            diffs = []
            for k in diff_position:
                diffs.append("{: 4} * 108 + {: 3}".format(k // 108, k % 108))


            print("mc {: 3} base vs inv {: 3} differ at".format(mc, i), "[{}]".format(", ".join(diffs)), "values changed from", a, "->", b)

def decode_usercode(data):
    data = data[0] # usercode is in FB 0

    bits = []

    for row in range(6, 8):
        for col in range(8):
            bits.append(data[108 * row + 8 * col + 7])
            bits.append(data[108 * row + 8 * col + 6])

    return bytes(np.packbits(bits)).decode("ascii")


def fuzz_interconnect(base):
    order = """
route_single_no_wysiwyg_2_3_to_1_1.jed
route_single_no_wysiwyg_4_17_to_1_1.jed
route_single_no_wysiwyg_2_18_to_1_1.jed
route_single_no_wysiwyg_4_15_to_1_1.jed
route_single_no_wysiwyg_2_4_to_1_1.jed
route_single_no_wysiwyg_2_1_to_1_1.jed
route_single_no_wysiwyg_2_2_to_1_1.jed
route_single_no_wysiwyg_4_16_to_1_1.jed
route_single_no_wysiwyg_2_5_to_1_1.jed
route_single_no_wysiwyg_4_13_to_1_1.jed
route_single_no_wysiwyg_2_6_to_1_1.jed
route_single_no_wysiwyg_4_12_to_1_1.jed
route_single_no_wysiwyg_2_8_to_1_1.jed
route_single_no_wysiwyg_4_10_to_1_1.jed
route_single_no_wysiwyg_4_18_to_1_1.jed
route_single_no_wysiwyg_2_10_to_1_1.jed
route_single_no_wysiwyg_4_14_to_1_1.jed
route_single_no_wysiwyg_2_7_to_1_1.jed
route_single_no_wysiwyg_4_7_to_1_1.jed
route_single_no_wysiwyg_2_11_to_1_1.jed
route_single_no_wysiwyg_4_6_to_1_1.jed
route_single_no_wysiwyg_2_12_to_1_1.jed
route_single_no_wysiwyg_4_11_to_1_1.jed
route_single_no_wysiwyg_2_13_to_1_1.jed
route_single_no_wysiwyg_4_4_to_1_1.jed
route_single_no_wysiwyg_2_14_to_1_1.jed
route_single_no_wysiwyg_2_16_to_1_1.jed
route_single_no_wysiwyg_4_8_to_1_1.jed
route_single_no_wysiwyg_2_15_to_1_1.jed
route_single_no_wysiwyg_4_5_to_1_1.jed
route_single_no_wysiwyg_2_17_to_1_1.jed
route_single_no_wysiwyg_4_2_to_1_1.jed
route_single_no_wysiwyg_1_2_to_1_1.jed
route_single_no_wysiwyg_4_9_to_1_1.jed
route_single_no_wysiwyg_1_5_to_1_1.jed
route_single_no_wysiwyg_4_1_to_1_1.jed
route_single_no_wysiwyg_1_6_to_1_1.jed
route_single_no_wysiwyg_3_16_to_1_1.jed
route_single_no_wysiwyg_3_13_to_1_1.jed
route_single_no_wysiwyg_1_8_to_1_1.jed
route_single_no_wysiwyg_3_12_to_1_1.jed
route_single_no_wysiwyg_1_3_to_1_1.jed
route_single_no_wysiwyg_3_10_to_1_1.jed
route_single_no_wysiwyg_1_4_to_1_1.jed
route_single_no_wysiwyg_3_18_to_1_1.jed
route_single_no_wysiwyg_1_9_to_1_1.jed
route_single_no_wysiwyg_3_17_to_1_1.jed
route_single_no_wysiwyg_1_11_to_1_1.jed
route_single_no_wysiwyg_3_15_to_1_1.jed
route_single_no_wysiwyg_1_7_to_1_1.jed
route_single_no_wysiwyg_3_14_to_1_1.jed
route_single_no_wysiwyg_1_14_to_1_1.jed
route_single_no_wysiwyg_3_7_to_1_1.jed
route_single_no_wysiwyg_1_10_to_1_1.jed
route_single_no_wysiwyg_3_6_to_1_1.jed
route_single_no_wysiwyg_1_15_to_1_1.jed
route_single_no_wysiwyg_3_11_to_1_1.jed
route_single_no_wysiwyg_1_17_to_1_1.jed
route_single_no_wysiwyg_3_4_to_1_1.jed
route_single_no_wysiwyg_3_2_to_1_1.jed
route_single_no_wysiwyg_3_3_to_1_1.jed
route_single_no_wysiwyg_3_9_to_1_1.jed
route_single_no_wysiwyg_3_5_to_1_1.jed
route_single_no_wysiwyg_3_1_to_1_1.jed
route_single_no_wysiwyg_1_13_to_1_1.jed
route_single_no_wysiwyg_1_18_to_1_1.jed
route_single_no_wysiwyg_3_8_to_1_1.jed
route_single_no_wysiwyg_1_16_to_1_1.jed
    """.split()

#    print(len(order))

    old = order[0]
    for f in order[1:]:
        diff_position, a, b = diff(base + old, base + f)

            # print(mc, i)
            # print(diff_position)

        diffs = []
        for k in diff_position:
            diffs.append("{: 4} * 108 + {: 3}".format(k // 108, k % 108))


        old_name = old.replace("route_single_no_wysiwyg_", "")
        old_name = old_name.replace("_to_1_1.jed", "")

        new_name = f.replace("route_single_no_wysiwyg_", "")
        new_name = new_name.replace("_to_1_1.jed", "")

        print("{: <7} vs {: <7} differ at".format(old_name, new_name), "[{}]".format(", ".join(diffs)), "values changed from", a, "->", b)

        old = f


def fuzz_interconnect2(base):
    (order, _) = subprocess.Popen(["sh", "-c", "for i in $(seq 1 1000); do grep -lE  '((FB_IMUX_INDEX \| FOOBAR1_ )|(-1) )\| '$i'($| )' out/route_single_small*.vm6; done"], stdout=subprocess.PIPE).communicate()
    order = order.decode("ascii")
    order = list(map(lambda f: f[:-3] + "jed", order.split()))

#    print(len(order))

    old = order[0]
    for f in order[1:]:
        diff_position, a, b = diff(old, f)

            # print(mc, i)
            # print(diff_position)

        diffs = []
        for k in diff_position:
            diffs.append("{: 4} * 108 + {: 3}".format(k // 108, k % 108))


        old_name = old.replace("out/route_single_small_", "")
        old_name = old_name.replace("_to_1_1.jed", "")

        new_name = f.replace("out/route_single_small_", "")
        new_name = new_name.replace("_to_1_1.jed", "")

        print("{: <7} vs {: <7} differ at".format(old_name, new_name), "[{}]".format(", ".join(diffs)), "values changed from", a, "->", b)

        old = f

def fuzz_interconnect3(base):
    (order, _) = subprocess.Popen(["sh", "-c", "for i in $(seq 1 1000); do grep -lE  '((FB_IMUX_INDEX \| FOOBAR1_ )|(-1) )\| '$i'($| )' out/route_single_big*.vm6; done"], stdout=subprocess.PIPE).communicate()
    order = order.decode("ascii")
    order = list(map(lambda f: f[:-3] + "jed", order.split()))

#    print(len(order))

    old = order[0]
    for f in order[1:]:
        diff_position, a, b = diff(old, f)

            # print(mc, i)
            # print(diff_position)

        diffs = []
        for k in diff_position:
            diffs.append("{: 4} * 108 + {: 3}".format(k // 108, k % 108))


        old_name = old.replace("out/route_single_big_", "")
        old_name = old_name.replace("_to_1_1.jed", "")

        new_name = f.replace("out/route_single_big_", "")
        new_name = new_name.replace("_to_1_1.jed", "")

        print("{: <7} vs {: <7} differ at".format(old_name, new_name), "[{}]".format(", ".join(diffs)), "values changed from", a, "->", b)

        old = f


if __name__ == "__main__":
    # fuzz_and_array_xor("out/")
    # fuzz_and_array("out/")
    fuzz_interconnect3("out/")

#    base = "out/"
#    for mc in range(18):
#        mc += 1
#        for i in range(0,54):
#            i += 1
#
#            diff_position, a, b = diff(base + str(mc) + "_0_xor.jed", base + str(mc) + "_{}_xor.jed".format(i))
#            m, n = diff_position
#
#            print("xor mc {: 3} base vs inv {: 3} differ at".format(mc, i), "[{: 4} * 108 + {: 3}, {: 4} * 108 + {: 3}]".format(m // 108, m % 108, n // 108, n % 108), "values changed from", a, "->", b)
