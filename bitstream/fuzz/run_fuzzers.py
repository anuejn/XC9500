import threading
from glob import glob
from os.path import join, dirname
import re
from inspect import isfunction
from subprocess import CalledProcessError
from sys import stderr
from time import sleep
from json import dumps

from infra import ise

DEVICE = "xc9536xl-5-VQ64"
MAX_THREADS = 10


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


def exec_testcase(testcase, jedecs):
    vhdl, ucf, labels = testcase
    try:
        jedecs[dumps(testcase)] = ise.synth(DEVICE, vhdl, ucf)
        print(".", end="")
    except CalledProcessError as err:
        jedecs[dumps(testcase)] = err
        print("e", end="", file=stderr)


if __name__ == "__main__":
    testcases = collect_testcases()

    print("\nrunning testcases...")

    results = {}
    threads = []
    for testcase in testcases:
        sleep(0.2)
        while len(threads) >= MAX_THREADS:
            sleep(0.1)
            threads = [t for t in threads if t.is_alive()]
        t = threading.Thread(target=exec_testcase, args=(testcase, results))
        t.start()
        threads.append(t)
    for thread in threads:
        while thread.is_alive():
            sleep(0.1)

    print("\nerrors:")
    for key, value in results.items():
        if not isinstance(value, str):
            print(value, value.output, "\n")
