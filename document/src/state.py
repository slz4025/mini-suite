from typing import Dict
import uuid

from src.entry import Entry


entries: Dict[str, Entry] = {}
init_entry_id = None


def get_entry(entry_id):
    if entry_id not in entries:
        return None
    return entries[entry_id]


def get_entry_id(file_path):
    path_to_id = {v.file_path: v.id for v in entries.values()}
    if file_path not in path_to_id:
        return None
    return path_to_id[file_path]


def add_entry(file_path):
    entry_id = uuid.uuid4().hex

    global entries
    entries[entry_id] = Entry(entry_id, file_path)

    return entry_id


def setup(file_path):
    global init_entry_id
    init_entry_id = add_entry(file_path)


def get_init_entry_id():
    return init_entry_id
