from flask import send_from_directory
import os
import uuid

import src.block as block
import src.errors as errors
import src.wiki as wiki


TEMP_DIR = os.path.expanduser("/tmp/minisuite/documents")
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

IS_TEMP = None
ENTRY = None


def get_name():
    if IS_TEMP:
        return None
    return ENTRY


def get_dir():
    if IS_TEMP:
        base = TEMP_DIR
    else:
        base = wiki.get()

    dir = os.path.join(base, ENTRY)
    return dir


def set_contents(session):
    dir = get_dir()
    filepath = os.path.join(dir, "index.md")
    with open(filepath, 'r') as file:
        markdown = file.read()

    block.set_all_markdown(session, markdown)


def use_temp(session):
    temp_name = uuid.uuid4().hex
    dir = os.path.join(TEMP_DIR, temp_name)
    os.makedirs(dir)

    indexpath = os.path.join(dir, "index.md")
    file = open(indexpath, 'w+')
    file.close()

    mediadir = os.path.join(dir, "media")
    os.makedirs(mediadir)

    global ENTRY, IS_TEMP
    ENTRY = temp_name
    IS_TEMP = True

    set_contents(session)


def check_name(name):
    if name == '':
        raise errors.UserError("Entry name was not given.")


def set(session, name):
    check_name(name)

    global ENTRY, IS_TEMP
    ENTRY = name
    IS_TEMP = False

    set_contents(session)


def save(session, name):
    check_name(name)

    markdown = block.get_all_markdown(session)

    dir = get_dir()
    index_path = os.path.join(dir, "index.md")
    with open(index_path, 'w+') as file:
        file.write(markdown)

    if IS_TEMP:
        dir = get_dir()
        wiki.move(dir, name)
    elif name != ENTRY:
        wiki.rename(ENTRY, name)


def import_file(session, file):
    filename = file.filename
    if not filename.endswith(".md"):
        raise errors.UserError("File is not a markdown file.")

    contents = file.read().decode("utf-8")
    block.set_all_markdown(session, contents)


def get_media(session, media_name):
    dir = get_dir()
    media_dir = os.path.join(dir, "media")
    media_path = os.path.join(media_dir, media_name)

    if not os.path.exists(media_path):
        raise errors.UserError(f"Media file does not exist: {media_name}.")

    return send_from_directory(media_dir, media_name)


def save_media(session, file):
    filename = file.filename
    _, extension = os.path.splitext(filename)
    contents = file.read()

    media_id = uuid.uuid4().hex
    media_name = f"{media_id}{extension}"

    dir = get_dir()
    media_dir = os.path.join(dir, "media")
    media_path = os.path.join(media_dir, media_name)

    with open(media_path, 'wb+') as media_file:
        media_file.write(contents)

    return media_name
