import contextlib


def get_app_class(app):
    # Is this a flask or celery application?
    with contextlib.suppress(AttributeError):
        _ = app.run
        return "flask"

    with contextlib.suppress(AttributeError):
        _ = app.control.inspect
        return "celery"

    return None
