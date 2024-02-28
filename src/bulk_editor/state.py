def get_selection_mode(session):
    if "bulk-editor-selection-mode" not in session:
        return None
    return session["bulk-editor-selection-mode"]


def set_selection_mode(session, selection_mode):
    session["bulk-editor-selection-mode"] = selection_mode


def reset_selection_mode(session):
    if "bulk-editor-selection-mode" in session:
        session.pop("bulk-editor-selection-mode")


def get_operation(session):
    if "bulk-editor-operation" not in session:
        return None
    return session["bulk-editor-operation"]


def set_operation(session, operation):
    session["bulk-editor-operation"] = operation


def reset_operation(session):
    if "bulk-editor-operation" in session:
        session.pop("bulk-editor-operation")


def get_buffer_selection_mode(session):
    if "buffer-selection-mode" not in session:
        return None
    return session["buffer-selection-mode"]


def set_buffer_selection_mode(session, selection_mode):
    session["buffer-selection-mode"] = selection_mode
