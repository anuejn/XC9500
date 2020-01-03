from multiprocessing import Pool
from collections import defaultdict
from glob import glob
from infra.util import cpu_count
from os.path import join, dirname
import re
from inspect import isfunction
from sys import stderr
from time import sleep
from json import dumps, dump

import numpy as np

from infra import ise, jed

DEVICE = "xc9536xl-5-VQ64"
MAX_THREADS = cpu_count()


def collect_testcases():
    testcases = []

    module_names = [re.match(".*/(\\w*)\\.py", x).group(1) for x in glob(join(dirname(__file__), "fuzzers", "*.py"))]
    modules = [getattr(__import__("fuzzers.{}".format(x)), x) for x in module_names]
    for module in modules:
        functions = [getattr(module, x) for x in dir(module) if
                     not x.startswith("__") and isfunction(getattr(module, x))]
        for function in functions:
            function_testcases = list(function(device=DEVICE))
            for testcase in function_testcases:
                testcases.append(testcase)
            print("collected {} testcases from {}.{}()".format(len(function_testcases), module.__name__,
                                                               function.__name__))
    print("collected a total of {} testcases from {} files".format(len(testcases), len(modules)))
    return testcases


def exec_testcase(testcase):
    vhdl, ucf, labels = testcase
    try:
        ret = (testcase, ise.synth(DEVICE, vhdl, ucf))
        print(".", end="", flush=True)
        return ret
    except Exception as err:
        ret = (testcase, err)
        print("e", end="", file=stderr, flush=True)
        return ret


def run_tests(testcases):
    print("running with {} concurrent threads".format(MAX_THREADS))
    p = Pool(MAX_THREADS)

    return p.map(exec_testcase, testcases)

def write_database(results):
    successful_results = [(experiment, jed.parse(contents=result)) for experiment, result in results if isinstance(result, str)]
    database = defaultdict(set)
    for experiment, result in successful_results:
        vhdl, ucf, tags = experiment
        config, data = result
        for one_bit in np.nonzero(data)[0]:
            for tag in tags:
                database[str(one_bit)].add(tag)
    db_file = "database/{}.json".format(DEVICE)
    bitstream_len = len(successful_results[0][1][1])
    with open(db_file, "w") as f:
        dump({
            "bitstream_len": bitstream_len,
            "bits": {k: list(v) for k, v in database.items()}
        }, f, indent="\t")
    print("tagged {}/{} bits and wrote \"{}\"".format(len(database.items()), bitstream_len, db_file))


if __name__ == "__main__":
    print("\n# collecting testcases:")
    testcases = collect_testcases()

    print("\n# running testcases:")
    results = run_tests(testcases)

    print("\n\n# errors:")
    for experiment, result in results:
        if not isinstance(result, str):
            print(result, "\n")

    print("\n# writing database:")
    write_database(results)


