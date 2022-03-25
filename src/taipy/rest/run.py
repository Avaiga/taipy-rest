from .app import create_app


def run(*args, **kwargs):
    app = create_app(*args, **kwargs)
    return app.run(*args, **kwargs)
