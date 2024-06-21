import uuid

import src.notifications.types as types


id = None
message = None
mode = None


def get_id():
    return id


def get_notification():
    return mode, message


def set_error(error):
    global message
    global mode
    global id
    message = str(error)
    mode = types.Mode.ERROR
    id = uuid.uuid4().hex


def set_info(msg):
    global message
    global mode
    global id
    message = msg
    mode = types.Mode.INFO
    id = uuid.uuid4().hex


def reset():
    global message
    global mode
    global id
    message = ""
    mode = types.Mode.NONE
    id = None


def init():
    global message
    global mode
    message = ""
    mode = types.Mode.NONE
