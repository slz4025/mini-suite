def get_message(session):
    if "error-message" not in session:
        return None
    return session["error-message"]


def set_message(session, error_message):
    session["error-message"] = error_message
