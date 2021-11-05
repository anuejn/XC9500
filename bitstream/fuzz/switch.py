#!/usr/bin/env python3

from glob import glob
import typing
from json import load as load_json
import database
from infra.html_dump import gen_html_view, known
from infra.bitstream import split_into_functionblocks
import numpy as np
from collections import defaultdict
from bitstream import bitstream, imux
from pathlib import Path
import pickle
import infra.ise
from infra import jed

def initial_pterm_muxes():
    with open("database/and_xc9536xl-5-VQ64.json") as f:
        db = load_json(f)

    db = database.bit_db_to_tag_db(db)

    from_to_bits = defaultdict(set)
    for to_test_mc in range(1, 19):
        to_test = (1, to_test_mc)
        first = True

        for to_fb in range(1, 3):
            for to_mc in range(1, 19):
                if (to_fb, to_mc) == to_test:
                    continue
                name = "passthrough_full_from_FB{}_{}_to_FB{}_{}".format(to_fb, to_mc, *to_test)
                b = db['tags'][name] & db['tags']['passthrough_full_not_inverted']
                if first:
                    set_for_all = b
                    first = False
                else:
                    set_for_all = set_for_all & b

        for to_fb in range(1, 3):
            for to_mc in range(1, 19):
                if (to_fb, to_mc) == to_test:
                    continue
                name = "passthrough_full_from_FB{}_{}_to_FB{}_{}".format(to_fb, to_mc, *to_test)
                b = (db['tags'][name] & db['tags']['passthrough_full_not_inverted']).difference(set_for_all)

                data = np.zeros(2 * 108 * 108, dtype=np.uint8)
                data[[int(bit) for bit in b]] = 1
                data = split_into_functionblocks(data, 2, flat=True)
                bit_data = []
                for fb in range(2):
                    bit_data.append(np.concatenate(data[fb]))
                b = bit_data[0].nonzero()[0]

                and_array_input = None
                for bit in b:
                    pterm_bits = bitstream['mcs'][f'MC{18 * (to_test[0] - 1) + to_test[1]}']['product_terms']['PTa']['and_array']
                    if bit in pterm_bits.values():
                        assert and_array_input is None
                        and_array_input = bit

                if and_array_input is None:
                    print(f"None and_array_input: FB{to_fb} MC{to_mc} -> FB{to_test[0]} MC{to_test[1]}")
                else:
                    from_to_bits[((to_fb, to_mc), and_array_input // (2 * 108))].add(tuple(sorted(set(b).difference(set([and_array_input])))))

    pterm_to_source_and_bit = defaultdict(dict)
    bit_to_pterm_and_source = {}
    for (((from_fb, from_mc), pterm), bits) in sorted(from_to_bits.items(), key=lambda v: v[0][1] + list(v[1])[0][0] / 10000):
        bits = list(bits)
        assert len(bits) == 1
        bits = bits[0]
        source = (from_fb - 1) * 18 + from_mc - 1
        pterm_to_source_and_bit[pterm][source] = bits
        bit_to_pterm_and_source[bits] = (pterm, source)
        # print(f"FB{from_fb} MC{from_mc} [{source}] to FB1 pterm {pterm}: {print_bit(bits)}")

    return pterm_to_source_and_bit, bit_to_pterm_and_source

def print_bit(i):
    if isinstance(i, typing.Iterable):
        return str([print_bit(b) for b in sorted(i)])
    else:
        return f"{i // 108} + {i % 108}"

def encode_feedback(source):
    return source + 10000

def fb_mc(n):
    if n > 10000:
        n = n - 10000
        return f"Feedback FB{n // 18 + 1}_{n % 18 + 1}"
    else:
        return f"FB{n // 18 + 1}_{n % 18 + 1}"

def bits_for_tag(db, tag, full=False):
    bits = db['bitstream_len']
    fbs = bits // (108 * 108)
    data = np.zeros(bits, dtype=np.uint8)
    bits = db['tags'][tag]

    data[[int(bit) for bit in bits]] = 1

    data = split_into_functionblocks(data, fbs, flat=True)
    bit_data = []
    for fb in range(fbs):
        bit_data.append(np.concatenate(data[fb]))

    if full:
        return bit_data
    else:
        return set(np.concatenate(bit_data).nonzero()[0])

def used_pterms(bits, mc, input):
    device = '36'
    if mc >= 36:
        device = '72'
    if mc >= 72:
        device = '72'
    if mc >= 144:
        device = '144'
    if mc >= 288:
        device = '288'

    possible = set(bitstream[device]['mcs'][f'MC{mc + 1}']['product_terms'][f'PT{input}']['and_array'].values())
    set_ones = possible & bits
    return set([(bit // (2 * 108)) % 54 for bit in set_ones]), set_ones

def parse_switch(bits, fb, device):
    base = fb * 108 * 108
    switch_values = [0 for _ in range(54)]
    for bit in bits:
        bit = bit - base
        if bit // 108 >= 50 and bit // 108 <= 76 and (bit % 108) % 8 in [6, 7]:
            row = bit // 108 - 50
            off = bit % 108
            ab = off % 8 - 6
            p = off // 8
            switch_values[row + 27 * ab] += 1 << p

    config = []

    for i, v in enumerate(switch_values):
        if v != 0:
            config.append((i, imux["95" + device + "XL"][i][v]))

    return config

def switch_bits(bits, fb = None):
    if fb is None:
        bits = [bit % (108 * 108) for bit in bits]
    else:
        bits = [bit % (108 * 108) for bit in bits if bit // (108 * 108) == fb]
    return set(bit for bit in bits if bit // 108 >= 50 and bit // 108 <= 76)

def dump_html_for_tag(db, tag):
    bit_data = bits_for_tag(db, tag, full=True)
    fbs = len(bit_data)
    gen_html_view(f"{tag}.html", bit_data, [[]] * fbs, [known] * fbs, title=tag)

if __name__ == "__main__":
    with open("database/feedback_xc9536xl-5-VQ64.json") as f:
        db = load_json(f)

    db = database.bit_db_to_tag_db(db)

    if False:
        name = "feedback_from_FB1_3_to_FB1_1"
        data = np.zeros(2 * 108 * 108, dtype=np.uint8)
        bits = db['tags'][name]

        data[[int(bit) for bit in bits]] = 1

        data = split_into_functionblocks(data, 2, flat=True)
        bit_data = []
        for fb in range(2):
            bit_data.append(np.concatenate(data[fb]))
        gen_html_view(f"{name}.html", bit_data, [[], []], [known, {}, {}, {}], title=name)
    elif False:
        pterm_to_source_and_bit, bit_to_pterm_and_source = initial_pterm_muxes()

        with open("database/feedback_xc9536xl-5-VQ64.json") as f:
            db = load_json(f)

        db = database.bit_db_to_tag_db(db)

        from_to_bits = defaultdict(set)
        for to_test in range(18):
            first = True

            for from_a in range(36):
                if from_a == to_test:
                    continue

                name = f"feedback_from_{fb_mc(from_a)}_to_{fb_mc(to_test)}"
                b = db['tags'][name]

                # filter out some missing stuff
                if len(b) == 0:
                    continue
                if first:
                    set_for_all = b
                    first = False
                else:
                    set_for_all = set_for_all & b
            for from_a in range(36):
                if from_a == to_test:
                    continue

                name = f"feedback_from_{fb_mc(from_a)}_to_{fb_mc(to_test)}"
                b = db['tags'][name].difference(set_for_all)

                data = np.zeros(2 * 108 * 108, dtype=np.uint8)
                data[[int(bit) for bit in b]] = 1
                data = split_into_functionblocks(data, 2, flat=True)
                bit_data = []
                for fb in range(2):
                    bit_data.append(np.concatenate(data[fb]))
                b = set(np.concatenate(bit_data).nonzero()[0])
                if len(b) == 0:
                    print(f"broken data for {name}")
                    continue

                inputs = [from_a, from_a]
                pterms = []
                unk = []
                # print(name, b)

                and_array_input_to_fb_node = bitstream['mcs'][f'MC{from_a + 1}']['product_terms']['PTa']['and_array'].values()
                assert len(input_bit := set(and_array_input_to_fb_node) & set(b)) == 1
                input_bit = list(input_bit)[0]
                b.remove(input_bit)
                input_pterm = input_bit // (108 * 2)
                # print(f"{name}: found input pterm {input_pterm}, {pterm_to_source_and_bit[input_pterm]}, {b}")

                if from_a < 18:
                    if from_a in pterm_to_source_and_bit[input_pterm]:
                        bits = pterm_to_source_and_bit[input_pterm][from_a]
                        assert all([bit in b for bit in bits])
                        for bit in bits:
                            b.remove(bit)
                    else:
                        print(f"cannot resolve pterm input mux from {fb_mc(from_a)} to pterm {input_pterm}")
                        continue

                and_array_input_to_output_node = bitstream['mcs'][f'MC{to_test + 1}']['product_terms']['PTa']['and_array'].values()
                assert len(input_bit := set(and_array_input_to_output_node) & set(b)) == 1
                output_bit = list(input_bit)[0]
                b.remove(output_bit)
                output_pterm = output_bit // (108 * 2)
                # print(f"{name}: found output pterm {input_pterm}, {pterm_to_source_and_bit[input_pterm]}, {b}")
                switch_bits = set(bit for bit in b if bit // 108 >= 50 and bit < 108 * 108)
                # all the bits for a specific pterm seem to be located in one row
                assert len(set(bit // 108 for bit in switch_bits)) == 1
                # print(f"[{name}] Feedback from {fb_mc(from_a)} to FB1 pterm {output_pterm}: {print_bit(switch_bits)}")
                encoded = encode_feedback(from_a)
                if encoded in (options := pterm_to_source_and_bit[output_pterm]):
                    assert options[encoded] == switch_bits
                else:
                    options[encoded] = switch_bits

        for pterm, options in sorted(pterm_to_source_and_bit.items(), key=lambda kv: kv[0]):
            print(f"pterm: {pterm}")
            for source, bits in sorted(options.items(), key=lambda kv: kv[0]):
                print(f"  {fb_mc(source)}: {print_bit(bits)}")
        Path("basic_pterms.pkl").write_bytes(pickle.dumps(pterm_to_source_and_bit))
    elif False:
        pterm_to_source_and_bit = pickle.loads(Path("basic_pterms.pkl").read_bytes())
        # there should be 4 * 54 / 72 = 3 options for each input
        # so lets find the ones that have less
        source_to_pterm = defaultdict(set)
        for pterm, options in pterm_to_source_and_bit.items():
            for source in options:
                source_to_pterm[source].add(pterm)
        for source, pterms in sorted(source_to_pterm.items()):
            print(f"{fb_mc(source)}, {pterms}")
        for source, pterms in sorted(source_to_pterm.items()):
            the_source = source
            if len(pterms) < 3:
                # ok we now want to discover a new option for this source
                # to force the fitter to show us a new option, we need to
                # force the fitter to use the pterms for which we know this source can be routed to for something else

                to_fill = set(pterms)
                filled = set()
                to_use = set([the_source])

                while len(to_fill) > 0:
                    pterm = to_fill.pop()

                    if pterm not in filled:
                        # print(f"we need to force {pterm} to be used")
                        other_sources = set(pterm_to_source_and_bit[pterm]) - to_use
                        # print(f"options for that are {[fb_mc(s) for s in other_sources]}")
                        # we want to find the source we can use to block this pterm with the least other options
                        # the ones in filled are already blocked by others, so we those are not valid options
                        source = sorted(other_sources, key=lambda k: len(source_to_pterm[k] - filled))[0]
                        # print(f"we will use {source}")
                        to_use.add(source)
                        for other_pterm in source_to_pterm[source]:
                            to_fill.add(other_pterm)


                    filled.add(pterm)

                print(f"should use {to_use}")

                possible_probes = set(range(18))
                left_over = possible_probes - set(s if s < 10000 else s - 10000 for s in to_use)
                probe_point = left_over.pop()
                feedback_input = left_over.pop()
                print(f"will use output on {probe_point}, dummy input for feedback on {feedback_input}")

                ucf = f'NET "feedback_input" LOC="{fb_mc(feedback_input)}"; NET "output" LOC = "{fb_mc(probe_point)}"; '
                stmt = ""
                feedback_ffs = ""
                signals = ""
                inputs = "feedback_input : in STD_LOGIC; output: out STD_LOGIC"
                for s in to_use:
                    if s > 10000:
                        s -= 10000
                        feedback_ffs += f"""
                            FDCE_inst{s}: FDCE
                            generic map (
                                INIT => '0'
                            )
                            port map (
                              Q => Q{s},
                              C => '0',
                              CE => '0',
                              CLR => '0',
                              D => feedback_input
                            );
                        """
                        ucf += f'INST "FDCE_inst{s}" KEEP=TRUE; INST "FDCE_inst{s}" LOC="{fb_mc(s)}"; '
                        stmt += f" and not Q{s}"
                        signals += f"signal Q{s}: STD_LOGIC;"
                    else:
                        ucf += f'NET "input{s}" LOC="{fb_mc(s)}"; '
                        stmt += f" and input{s}"
                        inputs += f"; input{s}: in STD_LOGIC"

                stmt = stmt[4:]
                VHDL = f"""
                    library IEEE;
                    use IEEE.STD_LOGIC_1164.ALL;
                    library unisim;
                    use UNISIM.vcomponents.ALL;

                    entity passthrough is
                        Port ({inputs});
                    end passthrough;

                    architecture Behavioral of passthrough is
                        {signals}
                    begin
                        {feedback_ffs}
                        output <= {stmt};
                    end Behavioral;
                """
                try:
                    out = infra.ise.synth("xc9536xl-5-VQ64", VHDL, ucf)
                    name = f"switch_{probe_point}_{feedback_input}_" + "_".join(map(str, to_use))
                    Path(name + ".jed").write_text(out)
                    bits = jed.parse(contents=out)[1]

                    data = split_into_functionblocks(bits, 2, flat=True)
                    bit_data = []
                    for fb in range(2):
                        bit_data.append(np.concatenate(data[fb]))
                    gen_html_view(f"{name}.html", bit_data, [[], []], [known, {}, {}, {}], title=name)
                except Exception as e:
                    print(e)
    elif False:
        pterm_to_source_and_bit = pickle.loads(Path("basic_pterms.pkl").read_bytes())
        # there should be 4 * 54 / 72 = 3 options for each input
        # so lets find the ones that have less
        source_to_pterm = defaultdict(set)
        for pterm, options in pterm_to_source_and_bit.items():
            print(f"pterm: {pterm}")
            for name, bits in options.items():
                print(f"  {name}: {print_bit(bits)}")

        for b in sorted(glob('switch*.jed'), key=len):
            bits = jed.parse(contents=Path(b).read_text())[1]
            b = b.removesuffix(".jed").split('_')
            output = int(b[1])
            feedback_input = int(b[2])
            inputs = [int(n) for n in b[3:]]

            data = split_into_functionblocks(bits, 2, flat=True)
            bit_data = []
            for fb in range(2):
                bit_data.append(np.concatenate(data[fb]))
            b = set(bit_data[0].nonzero()[0])

            pterm_inputs = []
            for bit in bitstream['mcs'][f'MC{output + 1}']['product_terms']['PTa']['and_array'].values():
                if bit in b:
                    b.remove(bit)
                    pterm_inputs.append(bit // (2 * 108))


            feedbacks_in_fb0 = [i for i in inputs if i < 10000 + 18 and i >= 10000]
            used_for_feedback = None
            for fb in feedbacks_in_fb0:
                possible = set(bitstream['mcs'][f'MC{fb - 10000 + 1}']['product_terms']['PTa']['and_array'].values())
                set_ones = possible & b
                assert len(set_ones) == 1
                pterm = set_ones.pop() // (2 * 108)
                if used_for_feedback is None:
                    used_for_feedback = pterm
                else:
                    assert used_for_feedback == pterm

            if used_for_feedback is not None:
                assert feedback_input in (options := pterm_to_source_and_bit[used_for_feedback])
                routing_bits = set(options[feedback_input])
                assert routing_bits.issubset(b)
                b.difference_update(routing_bits)


            # print(f"output {fb_mc(output)}")
            # print(f"feedback_input {fb_mc(feedback_input)}")
            # print(f"inputs: {inputs}")
            # print(f"used pterm inputs {sorted(pterm_inputs)}")

            switch_bits = set([])
            for bit in sorted(b):
                if bit // 108 >= 50 and bit // 108 < 78:
                    switch_bits.add(bit)
            # print(f"found switch bits {print_bit(switch_bits)}")

            # Ok now comes the difficult part. Somehow we have figure out which input got
            # routed to which pterm
            # Unfortunately the muxes are not encoded onehot, so a bit that might set a specific mux
            # to a specific configuration can also be part of other configurations of the same mux
            #
            # There are two simple cases:
            # A pterm was used for which we already know all configurations
            # Then we can exactly determine the configuration used and thus which input was used
            #
            # There are only two inputs. For one of the input pterms we should get a configuration we already
            # know (but we have to check in order of most bits set to least bits set)

            # Lets start with the first option
            to_consider = list(pterm_inputs)
            while len(to_consider) > 0:
                pterm = to_consider.pop()
                options = pterm_to_source_and_bit[pterm]
                # print(f"looking at pterm {pterm}")
                for source, bits in sorted(options.items(), key=lambda kv: len(kv[1]), reverse=True):
                    # print(f"known source config: {source}: {print_bit(bits)}")
                    bits = set(bits)
                    if bits.issubset(switch_bits):
                        if len(options) == 4:
                            assert source in inputs
                        if source in inputs:
                            inputs.remove(source)
                            pterm_inputs.remove(pterm)
                            switch_bits.difference_update(bits)
                        break
                else:
                    if len(options) == 4:
                        assert False
                    # print(f"did not find a matching configuration for {pterm}, we might learn something new :)")

            if len(pterm_inputs) <= 2:
                for pterm in pterm_inputs:
                    for source, bits in pterm_to_source_and_bit[pterm].items():
                        bits = set(bits)
                        if source in inputs and bits.issubset(switch_bits):
                            inputs.remove(source)
                            switch_bits.difference_update(bits)
                            pterm_inputs.remove(pterm)

                if len(pterm_inputs) == 1:
                    assert len(inputs) == 1
                    print(f"found new config {fb_mc(inputs[0])} to {pterm_inputs[0]}: {print_bit(switch_bits)}")
                    continue
            print()
            print(f"unable to resolve the following:")
            print(f"inputs: {inputs}")
            print(f"pterms used: {pterm_inputs}")
            print(f"switch bits: {print_bit(switch_bits)}")

    else:
        with open("database/xc9536xl-5-VQ64.json") as f:
            db = load_json(f)
            db = database.bit_db_to_tag_db(db)

            # dump_html_for_tag(db, "passthrough_from_FB4_11_to_FB1_1")

            for input in range(36):
                for output in range(18,36):
                    if input == output:
                        continue
                    for pp in ["feedback", "passthrough"]:
                        name = f"{pp}_from_{fb_mc(input)}_to_{fb_mc(output)}"
                        b = bits_for_tag(db, name)

                        if len(b) == 0:
                            # skip broken ones
                            continue

                        pterm, pterm_bits = used_pterms(b, output, 'a')
                        assert len(pterm) == 1
                        pterm = pterm.pop()
                        b -= pterm_bits
                        extra = ""
                        if pp == "feedback":
                            extra = "Feedback "
                        print(f"{name}: {extra}{fb_mc(input)} to pterm {pterm}: {print_bit(switch_bits(b, fb = output // 18))}")
