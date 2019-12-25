from jed import parse as parse_jed
import numpy as np

def parse_devicename(name):
    data = {}

    device, speedgrade, package = name.split("-")

    data["device"] = device
    data["speedgrad"] = speedgrade
    data["package"] = package

    submodel = int(device[4:6], 10)
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


def flat_bit_data(jed_file, fb=0):
    config, data = parse_jed(jed_file)

    device = parse_devicename(devicename_from_notes(config["notes"]))
    fb_data = split_into_functionblocks(data, device["function_blocks"], flat=True)
    bit_data = np.concatenate(fb_data[fb])

    return bit_data

def diff(a, b, fb=0):
    a_data = flat_bit_data(a, fb = fb)
    b_data = flat_bit_data(b, fb = fb)

    where = np.where(a_data != b_data)

    return (where[0], a_data[where], b_data[where])

def fuzz_and_array(base):
    for fb in range(1):
        fb = fb + 1
        for mc in range(1, 18):
            mc = mc + 1

            diff_position, a, b = diff(base + "1_01_to_{}_{:02}.jed".format(fb, mc), base + "1_01_to_{}_{:02}_inv.jed".format(fb, mc))
            print("1_01 to {}_{:02} differ at".format(fb, mc), diff_position, "values changed from", a, "->", b)


fuzz_and_array("out/")
