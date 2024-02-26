def get_selection_mode(session):
    if "bulk-edit-selection-mode" not in session:
        return None
    return session["bulk-edit-selection-mode"]


def set_selection_mode(session, selection_mode):
    session["bulk-edit-selection-mode"] = selection_mode


def reset_selection_mode(session):
    if "bulk-edit-selection-mode" in session:
        session.pop("bulk-edit-selection-mode")


def get_operation(session):
    if "bulk-edit-operation" not in session:
        return None
    return session["bulk-edit-operation"]


def set_operation(session, operation):
    session["bulk-edit-operation"] = operation


def reset_operation(session):
    if "bulk-edit-operation" in session:
        session.pop("bulk-edit-operation")


def get_buffer_selection_mode(session):
    if "buffer-selection-mode" not in session:
        return None
    return session["buffer-selection-mode"]


def set_buffer_selection_mode(session, selection_mode):
    session["buffer-selection-mode"] = selection_mode
