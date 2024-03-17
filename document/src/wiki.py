import os

import src.errors as errors


WIKI_PATH = None
entries = []


def get():
    return WIKI_PATH


def use(path):
    global entries
    directory_entries = os.listdir(path)
    for e in directory_entries:
        if os.path.isdir(os.path.join(path, e)):
            entries.append(e)


def set(path):
    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        raise errors.UserError(f"'{path}' is not a valid directory.")

    global WIKI_PATH
    WIKI_PATH = path
    use(path)


def exists(name):
    return name in entries


def add(name):
    entries.append(name)


def create(name):
    path = get()
    dir = os.path.join(path, name)
    os.makedirs(dir)

    indexpath = os.path.join(dir, "index.md")
    file = open(indexpath, 'w+')
    file.close()

    mediadir = os.path.join(dir, "media")
    os.makedirs(mediadir)

    add(name)
