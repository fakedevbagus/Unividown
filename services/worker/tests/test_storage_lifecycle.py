import os
import time
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.services import storage


def configure_roots(tmp_path, monkeypatch):
    upload = tmp_path / 'uploads'; download = tmp_path / 'downloads'; processed = tmp_path / 'processed'
    for root in (upload, download, processed): root.mkdir()
    monkeypatch.setattr(storage.settings, 'upload_dir', str(upload)); monkeypatch.setattr(storage.settings, 'download_dir', str(download)); monkeypatch.setattr(storage.settings, 'processed_dir', str(processed))
    return upload, download, processed


def test_storage_usage_and_quota(tmp_path, monkeypatch):
    upload, _, _ = configure_roots(tmp_path, monkeypatch)
    (upload / 'file.bin').write_bytes(b'12345')
    monkeypatch.setattr(storage.settings, 'storage_quota_bytes', 6)
    assert storage.storage_usage_bytes() == 5
    storage.ensure_storage_capacity(1)
    with pytest.raises(HTTPException) as error: storage.ensure_storage_capacity(2)
    assert error.value.status_code == 507


def test_cleanup_removes_expired_and_keeps_recent(tmp_path, monkeypatch):
    upload, _, processed = configure_roots(tmp_path, monkeypatch)
    old_file = upload / 'old.part'; recent_file = processed / 'recent.mp4'
    old_file.write_bytes(b'old'); recent_file.write_bytes(b'recent')
    now = time.time(); os.utime(old_file, (now - 7200, now - 7200))
    monkeypatch.setattr(storage.settings, 'output_retention_hours', 1)
    report = storage.cleanup_expired_storage(now=now)
    assert report.deleted_files == 1
    assert not old_file.exists(); assert recent_file.exists()


def test_zero_quota_disables_limit(tmp_path, monkeypatch):
    configure_roots(tmp_path, monkeypatch)
    monkeypatch.setattr(storage.settings, 'storage_quota_bytes', 0)
    storage.ensure_storage_capacity(10**12)
