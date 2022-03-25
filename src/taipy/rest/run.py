from .app import create_app


def run(testing=False, flask_env=None, secret_key=None, *args, **kwargs):
    app = create_app(testing, flask_env, secret_key)
    return app.run(*args, **kwargs)
