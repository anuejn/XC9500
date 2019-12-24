from tempfile import mkstemp
from subprocess import check_call


def tmpfile(content=None, suffix=None):
    filename = mkstemp(suffix=suffix)[1]
    if content is not None:
        exec("sh", args(c="cat << EOF > {filename}\n{content}\nEOF".format(content=content, filename=filename)))
    else:
        exec("touch", args(filename))
    return filename


def exec(executable, args=[], working_dir=None):
    command = [*(["cd", working_dir, "&&"] if working_dir else []), executable, *args]
    print(" ".join(command))


def args(*args, **kwargs):
    return [*[x for key in kwargs for x in ["-" + key, kwargs[key]]], *args]
