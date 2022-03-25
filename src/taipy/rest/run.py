from .app import create_app

app = create_app()


def run(debug=False):
    return app.run(debug=debug)
