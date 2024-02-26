# Errors that arise that we should have checks against on the client.
class ClientError(Exception):
    pass


# Errors that arise due to bad user input/action.
class UserError(Exception):
    pass


def get_error_message(session):
    if "error-message" not in session:
        return None
    return session["error-message"]


def set_error_message(session, error_message):
    session["error-message"] = error_message
