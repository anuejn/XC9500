from tempfile import mkstemp
from subprocess import check_call, check_output
from os import environ
from sys import stderr
from textwrap import dedent
import hashlib


def tmpfile(content=None, suffix=None):
    filename = mkstemp(suffix=suffix)[1]
    if content is not None:
        exec("sh", args(c="cat << EOF > {filename}\n{content}\nEOF".format(content=clean(content), filename=filename)))
    else:
        exec("touch", args(filename))
    return filename


def clean(str):
    return dedent(str).lstrip().rstrip()


def exec(executable, args=[], working_dir=None):
    command_string = " ".join([executable, *args])

    if working_dir:
        command_string = 'cd "{}" &&'.format(working_dir) + command_string

    if environ.get("EXEC_TEMPLATE"):
        command_string = environ["EXEC_TEMPLATE"].format(command_string)

    print(command_string, file=stderr)
    return check_output(command_string, shell=True)


def cat(filename):
    return exec("cat", args(filename))


def args(*args, **kwargs):
    return [*[x for key in kwargs for x in ["-" + key, kwargs[key]]], *args]
