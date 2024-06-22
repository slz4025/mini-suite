from typing import Dict
import uuid

from src.entry import Entry


entries: Dict[str, Entry] = {}


# TODO: temporary
def get_singleton():
    if len(entries) == 1:
        return [k for k in entries.keys()][0]
    return None


def get_entry(entry_id):
    if entry_id not in entries:
        return None
    return entries[entry_id]


def add_entry(file_path):
    entry_id = uuid.uuid4().hex

    global entries
    entries[entry_id] = Entry(entry_id, file_path)
