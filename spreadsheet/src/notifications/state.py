import src.notifications.types as types


message = None
mode = None


def get_notification():
    return mode, message


def set_error(error):
    global message
    global mode
    message = str(error)
    mode = types.Mode.ERROR


def set_info(msg):
    global message
    global mode
    message = msg
    mode = types.Mode.INFO


def reset():
    global message
    global mode
    message = ""
    mode = types.Mode.NONE


def init():
    global message
    global mode
    message = ""
    mode = types.Mode.NONE
