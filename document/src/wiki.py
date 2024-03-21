import os
import shutil

import src.errors as errors
import src.markdown as md


DOWNLOADS_PATH = os.path.expanduser("~/Downloads")
if not os.path.exists(DOWNLOADS_PATH):
    os.makedirs(DOWNLOADS_PATH)

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


def check_exists(name):
    if name not in entries:
        raise errors.UserError("Entry name does not exist in wiki.")


def add(name):
    entries.append(name)


def remove(name):
    entries.remove(name)


def create(name):
    wiki_path = get()
    dir = os.path.join(wiki_path, name)
    os.makedirs(dir)

    indexpath = os.path.join(dir, "index.md")
    file = open(indexpath, 'w+')
    file.close()

    mediadir = os.path.join(dir, "media")
    os.makedirs(mediadir)

    add(name)


def move(src_dir, dest_name):
    wiki_dir = get()
    dest_dir = os.path.join(wiki_dir, dest_name)

    # allow destructive overwrites
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
    else:
        add(dest_name)

    shutil.move(src_dir, dest_dir)


def rename(prev_name, new_name):
    wiki_dir = get()
    prev_dir = os.path.join(wiki_dir, prev_name)
    move(prev_dir, new_name)
    remove(prev_name)


def export(session, filename):
    if filename == '':
        raise errors.UserError("File name was not given.")

    wiki_path = get()

    export_dir = os.path.join(DOWNLOADS_PATH, filename)
    try:
        os.makedirs(export_dir)
    except OSError:
        raise errors.UserError(
                f"Download folder already has entry '{filename}'."
                )

    # only exports what is saved in current entry and others
    for entry in entries:
        if entry.startswith("temp-"):
            continue

        md_dir = os.path.join(wiki_path, entry)

        html_dir = os.path.join(export_dir, entry)
        os.makedirs(html_dir)

        md_indexpath = os.path.join(md_dir, "index.md")
        with open(md_indexpath, 'r') as file:
            markdown = file.read()

        html = md.html_for_external(markdown)

        html_indexpath = os.path.join(html_dir, "index.html")
        with open(html_indexpath, 'w+') as file:
            file.write(html)

        md_mediadir = os.path.join(md_dir, "media")
        html_mediadir = os.path.join(html_dir, "media")
        shutil.copytree(md_mediadir, html_mediadir)

    filepath = os.path.join(DOWNLOADS_PATH, filename)
    shutil.make_archive(filepath, 'zip', DOWNLOADS_PATH, export_dir)
