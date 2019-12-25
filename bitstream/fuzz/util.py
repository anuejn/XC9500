from subprocess import check_output
from os import environ
from sys import stderr
from textwrap import dedent
from hashlib import md5 as hash
import pickle
from os import path, makedirs


def tmpfile(content=None, hash_seed=None, suffix=None):
    if content:
        hash_seed = content
    assert hash_seed is not None, "when no content is provided, a hash seed is mandatory!"
    filename = "/tmp/{}".format(hash(hash_seed.encode("utf-8")).hexdigest(), suffix)
    if suffix:
        filename += suffix
    if content is not None:
        exec("sh", args(c="cat << EOF > {filename}\n{content}\nEOF".format(content=clean(content), filename=filename)))
    else:
        exec("touch", args(filename))
    return filename


def clean(str):
    return dedent(str).lstrip().rstrip()


def args(*args, **kwargs):
    return [*[x for key in kwargs for x in ["-" + key, kwargs[key]]], *args]


def exec(executable, args=None, working_dir=None, should_cache=True):
    if args is None:
        args = []
    command_string = " ".join([executable, *args])

    if working_dir:
        command_string = 'cd "{}" &&'.format(working_dir) + command_string

    if environ.get("EXEC_TEMPLATE"):
        command_string = environ["EXEC_TEMPLATE"].format(command_string)


    if should_cache:
        return cache(command_string, lambda: check_output(command_string, shell=True))
    else:
        print("[no cache]" + command_string, file=stderr)
        return check_output(command_string, shell=True)


def cat(filename, binary=False):
    content = exec("cat", args(filename))
    if not binary:
        content = content.decode("utf-8")
    return content


def cache(key, value_lambda, cache_path='./__pycache__/exec_cache.pickle'):
    def write(data):
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    def read():
        with open(cache_path, 'rb') as f:
            return pickle.load(f)

    if not path.exists(cache_path):
        makedirs(path.dirname(cache_path))
        write(dict())

    cache = read()
    if key not in cache:
        print("[cache miss] " + key, file=stderr)
        cache[key] = value_lambda()
        write(cache)
    else:
        print("[cache hit]  " + key, file=stderr)
    return cache[key]
