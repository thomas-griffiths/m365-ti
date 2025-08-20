import sys
from pathlib import Path

# Ensure src directory is on the path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from main import load_config, scan_and_tag


class DummyClient:
    """Minimal client for scan_and_tag tests."""
    def list_messages(self, user: str, top: int):
        return []

    def ensure_category(self, user: str, category: str):
        pass

    def tag_message(self, user: str, msg_id: str, category: str):
        pass

    def send_mail(self, user: str, summary_to: str, subject: str, html: str):
        pass


def test_load_config_missing_file(tmp_path):
    missing = tmp_path / "config.json"
    with pytest.raises(FileNotFoundError):
        load_config(missing)


def test_load_config_missing_keys(tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text('{"tenant_id": "t", "client_id": "c"}')
    with pytest.raises(ValueError, match="Missing required configuration keys"):
        load_config(cfg)


def test_scan_and_tag_invalid_user_email():
    with pytest.raises(ValueError, match="Invalid user email format"):
        scan_and_tag(DummyClient(), "bad-email", 10, "cat", False, None)


def test_scan_and_tag_collect_iocs_failure(monkeypatch):
    def boom():
        raise Exception("boom")

    monkeypatch.setattr("main.collect_iocs", boom)

    with pytest.raises(RuntimeError, match="Error collecting IoCs"):
        scan_and_tag(DummyClient(), "user@example.com", 10, "cat", False, None)


def test_scan_and_tag_invalid_summary_email():
    with pytest.raises(ValueError, match="Invalid summary email format"):
        scan_and_tag(DummyClient(), "user@example.com", 10, "cat", False, "bad-email")
