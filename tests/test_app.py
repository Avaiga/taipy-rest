from unittest import mock
from src.taipy.rest.app import create_app


def test_create_app_with_gui_installed():
    with mock.patch("src.taipy.rest.app.gui_installed") as mck_gui_installed:
        mck_gui_installed.return_value = True
        app = create_app()
        assert app.config["GUI"] is True


def test_create_app_without_gui_installed():
    with mock.patch("src.taipy.rest.app.gui_installed") as mck_gui_installed:
        mck_gui_installed.return_value = False
        app = create_app()
        assert app.config.get("GUI") is None
