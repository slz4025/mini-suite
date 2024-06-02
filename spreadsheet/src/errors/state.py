error_message = None

def get_message():
    return error_message

def set_message(err_msg):
    global error_message
    error_message = err_msg
