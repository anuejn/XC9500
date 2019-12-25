import numpy as np

# start of text
from util import cat

STX = chr(0x2)
# end of text
ETX = chr(0x3)


def parse(contents):
    config = {}

    comment, commands = contents.split(STX, 1)
    commands, checksum = commands.split(ETX, 1)

    config["comment"] = comment
    config["checksum"] = checksum

    for command in commands.split("*"):
        command = command.strip()

        if len(command) == 0:
            continue

        first = command[0]

        if first == "Q":
            if command[1] == "F":
                config["number_of_fuses"] = int(command[2:])
                data = np.unpackbits(np.zeros(config["number_of_fuses"] // 8, dtype=np.uint8))
            elif command[1] == "P":
                config["number_of_pins"] = int(command[2:])
            elif command[1] == "V":
                config["number_of_testvectors"] = int(command[2:])
        elif first == "F":
            config["default_state"] = int(command[1:])
            data[:] = config["default_state"]
        elif first == "X":
            config["default_test_condition"] = int(command[1:])
        elif first == "N":
            if "notes" in config:
                config["notes"].append(command[2:])
            else:
                config["notes"] = [command[2:]]
        elif first == "L":
            location, bits = command[1:].split(" ", 1)
            location = int(location, 10)
            bits = np.array([int(bit) for bit in bits.replace(" ", "")])
            data[location:location + len(bits)] = bits
        elif first == "C":
            config["checksum"] = int(command[1:], 16)
        elif first == "J":
            arch_code, pinout_code = command[1:].split(" ")
            config["architecture_code"] = int(arch_code, 10)
            config["pinout_code"] = int(pinout_code, 10)
        else:  # unknown
            print("unknown jedec command:", command)

    return config, data

