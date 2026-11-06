import urllib.request

import pytest


@pytest.fixture
def desktop():
    pytest.importorskip("webview")
    from app import desktop

    return desktop


def test_free_port_is_usable(desktop):
    assert 1024 < desktop.free_port() < 65536


def test_wait_until_ready_gives_up(desktop):
    assert not desktop.wait_until_ready(f"http://127.0.0.1:{desktop.free_port()}/", timeout=0.3)


def test_opens_a_window_on_the_running_app(desktop, monkeypatch):
    opened = {}

    def create_window(title, url, **options):
        opened["title"] = title
        opened["url"] = url

    def start():
        with urllib.request.urlopen(opened["url"]) as response:
            opened["status"] = response.status
            opened["page"] = response.read().decode()

    monkeypatch.setattr(desktop.webview, "create_window", create_window)
    monkeypatch.setattr(desktop.webview, "start", start)
    desktop.main()
    assert opened["title"] == "StudyAI"
    assert opened["status"] == 200
    assert "StudyAI" in opened["page"]
