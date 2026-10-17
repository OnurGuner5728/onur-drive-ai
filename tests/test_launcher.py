from onur_drive.launcher import HOST, PORT, open_dashboard_when_ready
from onur_drive.service import DASHBOARD


def test_stays_local_only():
    assert HOST == "127.0.0.1"
    assert PORT == 8765


def test_support_link_is_explicitly_optional():
    assert "https://www.patreon.com/c/onurguner" in DASHBOARD
    assert "rel='noopener noreferrer'" in DASHBOARD
    assert "tamamen isteğe bağlıdır" in DASHBOARD


def test_cannot_open_browser_without_a_server(monkeypatch):
    opened = []
    monkeypatch.setattr("onur_drive.launcher.webbrowser.open", opened.append)
    assert open_dashboard_when_ready(port=65534, max_wait_s=0.0) is False
    assert opened == []
