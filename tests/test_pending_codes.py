"""Tests for UserStore.generate_code / verify_code persistence.

The codes used to live in an in-memory dict on the UserStore instance,
which broke verification under multi-replica deploys (the replica handling
the webhook delivery for the typed code wasn't necessarily the one that
generated it). They now live on disk in a sibling JSON file so any replica
sees the same state.

These tests pin the on-disk shape, the cross-instance visibility, the
expiry behaviour, and the consume-on-success / consume-on-expiry deletes.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from core.auth import UserStore


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def store(tmp_path):
    """Fresh store rooted at a tmp dir per test — no shared state."""
    return UserStore(tmp_path / "users.json")


def test_generate_code_persists_to_disk(store, tmp_path):
    code = _run(store.generate_code("whatsapp", "420123456789", "a@b.cz"))
    assert code.isdigit() and len(code) == 6

    pending_path = tmp_path / "pending_codes.json"
    assert pending_path.exists()
    data = json.loads(pending_path.read_text(encoding="utf-8"))
    record = data["whatsapp:420123456789"]
    assert record["email"] == "a@b.cz"
    assert record["code"] == code
    assert isinstance(record["created_at"], (int, float))


def test_verify_code_succeeds_with_matching_code_and_consumes_entry(store, tmp_path):
    code = _run(store.generate_code("telegram", "777", "a@b.cz"))

    result = _run(store.verify_code("telegram", "777", code))
    assert result == "a@b.cz"

    # Entry should be deleted after a successful match.
    data = json.loads((tmp_path / "pending_codes.json").read_text(encoding="utf-8"))
    assert "telegram:777" not in data


def test_verify_code_fails_with_wrong_code_and_keeps_entry(store, tmp_path):
    code = _run(store.generate_code("telegram", "777", "a@b.cz"))
    wrong = "000000" if code != "000000" else "111111"

    result = _run(store.verify_code("telegram", "777", wrong))
    assert result is None

    # On a wrong code we KEEP the entry so the user can retry.
    data = json.loads((tmp_path / "pending_codes.json").read_text(encoding="utf-8"))
    assert "telegram:777" in data
    assert data["telegram:777"]["code"] == code


def test_verify_code_returns_none_when_no_pending(store):
    result = _run(store.verify_code("telegram", "no-such-user", "123456"))
    assert result is None


def test_verify_code_expired_returns_none_and_consumes_entry(store, tmp_path):
    code = _run(store.generate_code("whatsapp", "999", "a@b.cz"))

    # Rewind the stored timestamp so the entry is older than the expiry.
    pending_path = tmp_path / "pending_codes.json"
    data = json.loads(pending_path.read_text(encoding="utf-8"))
    data["whatsapp:999"]["created_at"] = time.time() - (15 * 60)  # 15 min ago
    pending_path.write_text(json.dumps(data), encoding="utf-8")

    result = _run(store.verify_code("whatsapp", "999", code, expiry_minutes=10))
    assert result is None

    # Expired entries should be cleaned up.
    data = json.loads(pending_path.read_text(encoding="utf-8"))
    assert "whatsapp:999" not in data


def test_verify_code_strips_whitespace_in_input(store):
    code = _run(store.generate_code("telegram", "777", "a@b.cz"))
    assert _run(store.verify_code("telegram", "777", f"  {code}  ")) == "a@b.cz"


def test_two_store_instances_share_pending_codes_via_disk(tmp_path):
    """The whole point of the change: codes written by one process / replica
    are readable by another instance pointing at the same data dir."""
    s1 = UserStore(tmp_path / "users.json")
    s2 = UserStore(tmp_path / "users.json")  # different instance, same files

    code = _run(s1.generate_code("whatsapp", "420111", "a@b.cz"))
    # s2 has its own in-memory state but reads from the same disk.
    assert _run(s2.verify_code("whatsapp", "420111", code)) == "a@b.cz"

    # And the consume happens on disk — s1 also sees it gone.
    assert _run(s1.verify_code("whatsapp", "420111", code)) is None


def test_pending_codes_file_starts_missing_and_returns_none_cleanly(tmp_path):
    """A fresh data dir has no pending_codes.json. verify_code must not blow up."""
    store = UserStore(tmp_path / "users.json")
    assert not (tmp_path / "pending_codes.json").exists()
    assert _run(store.verify_code("telegram", "999", "123456")) is None


def test_pending_codes_corrupt_file_recovered_on_next_write(tmp_path):
    """If the pending_codes.json is corrupted (e.g. partial write from a
    pre-atomic-write era), reads should treat it as empty — not crash.
    A subsequent generate_code rewrites the file cleanly."""
    pending_path = tmp_path / "pending_codes.json"
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    pending_path.write_text("{ this is not json", encoding="utf-8")

    store = UserStore(tmp_path / "users.json")
    code = _run(store.generate_code("telegram", "777", "a@b.cz"))
    data = json.loads(pending_path.read_text(encoding="utf-8"))
    assert data["telegram:777"]["code"] == code


def test_independent_users_do_not_collide(store):
    a_code = _run(store.generate_code("telegram", "111", "a@b.cz"))
    b_code = _run(store.generate_code("telegram", "222", "x@y.cz"))

    assert _run(store.verify_code("telegram", "111", b_code)) is None
    assert _run(store.verify_code("telegram", "222", a_code)) is None
    assert _run(store.verify_code("telegram", "111", a_code)) == "a@b.cz"
    assert _run(store.verify_code("telegram", "222", b_code)) == "x@y.cz"
