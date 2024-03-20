from flask import send_from_directory
import os
import shutil
import uuid

import src.block as block
import src.errors as errors
import src.wiki as wiki


ENTRY = None


def istemp():
    return ENTRY.startswith("temp-")


def create_temp_name():
    return "temp-{}".format(uuid.uuid4().hex)


def get(allow_temp=True):
    if not allow_temp and istemp():
        return None
    return ENTRY


def check(name):
    if name == '':
        raise errors.UserError("Entry name was not given.")
    if not wiki.exists(name):
        raise errors.UserError("Entry name does not exist in wiki.")


def set(session, name):
    check(name)

    global ENTRY
    ENTRY = name

    wiki_dir = wiki.get()

    filepath = os.path.join(wiki_dir, name, "index.md")
    with open(filepath, 'r') as file:
        contents = file.read()

    block.set_all_markdown(session, contents)


def use_temp(session):
    temp_name = create_temp_name()
    wiki.create(temp_name)
    set(session, temp_name)


def save(session, name):
    if name == '':
        raise errors.UserError("Entry name was not given.")
    if name.startswith("temp-"):
        raise errors.UserError(f"Name cannot start with 'temp-': {name}.")

    if not wiki.exists(name):
        wiki.create(name)
    wiki_dir = wiki.get()

    current_entry = get()
    curr_dir = os.path.join(wiki_dir, current_entry)

    index_path = os.path.join(curr_dir, "index.md")
    markdown = block.get_all_markdown(session)
    with open(index_path, 'w+') as file:
        file.write(markdown)

    if name != current_entry:
        new_dir = os.path.join(wiki_dir, name)
        # allow destructive overwrites
        if os.path.isdir(new_dir):
            shutil.rmtree(new_dir)
        shutil.move(curr_dir, new_dir)


def import_file(session, file):
    filename = file.filename
    if not filename.endswith(".md"):
        raise errors.UserError("File is not a markdown file.")

    contents = file.read().decode("utf-8")
    block.set_all_markdown(session, contents)


def get_media(session, filename):
    wiki_dir = wiki.get()
    current_entry = get()

    media_folder = os.path.join(wiki_dir, current_entry, "media")
    filepath = os.path.join(media_folder, filename)
    if not os.path.exists(filepath):
        raise errors.UserError(f"Media file does not exist: {filename}.")

    return send_from_directory(media_folder, filename)


def save_media(session, file):
    wiki_dir = wiki.get()
    current_entry = get()
    media_folder = os.path.join(wiki_dir, current_entry, "media")

    filename = file.filename
    _, extension = os.path.splitext(filename)
    media_id = uuid.uuid4().hex
    mediapath = f"{media_id}{extension}"

    filepath = os.path.join(media_folder, mediapath)
    contents = file.read()
    with open(filepath, 'wb+') as media_file:
        media_file.write(contents)

    return mediapath