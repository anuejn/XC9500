import threading
from subprocess import check_output, CalledProcessError, Popen, PIPE
from os import environ
from textwrap import dedent
from hashlib import md5 as hash
import json
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

    def real_exec():
        pipes = Popen(command_string, shell=True, stdout=PIPE, stderr=PIPE)
        std_out, std_err = pipes.communicate()
        if pipes.returncode == 0:
            return std_out.decode("utf-8")
        else:
            raise CalledProcessError(pipes.returncode, command_string, std_err)

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


def cache(key, value_lambda, cache_path='./__pycache__/exec_cache.json', cachefile_lock=threading.Lock()):
    key_hash = hash(key.encode("utf-8")).hexdigest()

    def write(data):
        cachefile_lock.acquire()
        with open(cache_path, 'w') as f:
            json.dump(data, f)
        cachefile_lock.release()

    def read():
        cachefile_lock.acquire()
        with open(cache_path, 'r') as f:
            content = json.load(f)
        cachefile_lock.release()
        return content

    if not path.exists(cache_path):
        makedirs(path.dirname(cache_path))
        write(dict())

    cache = read()
    if key_hash not in cache:
        cache[key_hash] = value_lambda()
        write(cache)
    else:
        # print("[cache hit ] " + key, file=stderr)
        pass
    return cache[key_hash]
