def get_operation(session):
    if "bulk-editor-operation" not in session:
        return None
    return session["bulk-editor-operation"]


def set_operation(session, operation):
    session["bulk-editor-operation"] = operation


def reset_operation(session):
    if "bulk-editor-operation" in session:
        session.pop("bulk-editor-operation")
