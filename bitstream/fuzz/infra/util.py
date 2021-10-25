import threading
from os.path import dirname, exists
from subprocess import check_output, CalledProcessError, Popen, PIPE
from os import environ, makedirs
from sys import stderr
from textwrap import dedent
from hashlib import md5 as hash
from base64 import b64encode
import pickle
import atexit

def cpu_count():
    return int(exec("sh", args(c="\"python3 -c 'import os; print(os.cpu_count())'\"")))

def tmpfile(content=None, hash_seed=None, suffix=None):
    if content is not None:
        hash_seed = content
    assert hash_seed is not None, "when no content is provided, a hash seed is mandatory!"

    filename = "/tmp/{}".format(hash(hash_seed.encode("utf-8")).hexdigest(), suffix)
    if suffix:
        filename += suffix

    if content is not None:
        content = clean(content)
        content = b64encode(content.encode("utf-8")).decode("utf-8")

        exec("sh", args(c="\"echo {content} | base64 -d > {filename}\"".format(content=content, filename=filename)))
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

    def real_exec():
        pipes = Popen(command_string, shell=True, stdout=PIPE, stderr=PIPE)
        std_out, std_err = pipes.communicate()
        if pipes.returncode == 0:
            return std_out.decode("utf-8")
        else:
            raise CalledProcessError(pipes.returncode, command_string, std_out.decode("utf-8"), std_err.decode("utf-8"))

    if should_cache:
        return cache(command_string, real_exec)
    else:
        # print("[no cache]" + command_string, file=stderr)
        return real_exec()


def cat(filename, binary=False):
    content = exec("cat", args(filename))
    if not binary:
        content = content
    return content


def cache(key, value_lambda, cache_path='./.cache/exec_cache.pickle', cache_map={}):
    key_hash = hash(key.encode("utf-8")).hexdigest()

    def save():
        if not exists(dirname(cache_path)):
            makedirs(dirname(cache_path))
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_map, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load():
        with open(cache_path, 'rb') as f:
            content = pickle.load(f)
        return content

    if len(cache_map.items()) == 0:
        if exists(cache_path):
            cache_map.update(load())
    atexit.register(save)

    if key_hash not in cache_map:
        cache_map[key_hash] = value_lambda()
    return cache_map[key_hash]
