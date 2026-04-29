"""Tests for UserStore.generate_code / verify_code persistence.

The codes used to live in an in-memory dict on the UserStore instance,
which broke verification under multi-replica deploys (the replica handling
the typed code's webhook wasn't necessarily the one that generated it).

They now live on disk as one file per user under a sibling pending_codes/
directory. Per-file storage means concurrent writers for different users
never touch the same file — two replicas can't clobber each other's
pending records, and Azure Files SMB handles per-file ops cleanly.

These tests pin the on-disk layout, the cross-instance visibility, the
expiry behaviour, the consume-on-success / consume-on-expiry deletes,
and graceful handling of missing / corrupted / malformed records.
"""

from __future__ import annotations

import asyncio
import json
import time

import pytest

from core.auth import UserStore


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def store(tmp_path):
    """Fresh store rooted at a tmp dir per test — no shared state."""
    return UserStore(tmp_path / "users.json")


def _pending_file(tmp_path, channel_type: str, channel_id: str):
    safe = f"{channel_type}_{channel_id}".replace(":", "_")
    return tmp_path / "pending_codes" / f"{safe}.json"


def test_generate_code_persists_one_file_per_user(store, tmp_path):
    code = _run(store.generate_code("whatsapp", "420123456789", "a@b.cz"))
    assert code.isdigit() and len(code) == 6

    path = _pending_file(tmp_path, "whatsapp", "420123456789")
    assert path.exists()
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["email"] == "a@b.cz"
    assert record["code"] == code
    assert isinstance(record["created_at"], (int, float))


def test_verify_code_succeeds_and_consumes_entry(store, tmp_path):
    code = _run(store.generate_code("telegram", "777", "a@b.cz"))
    path = _pending_file(tmp_path, "telegram", "777")

    result = _run(store.verify_code("telegram", "777", code))
    assert result == "a@b.cz"
    assert not path.exists()


def test_verify_code_fails_with_wrong_code_and_keeps_entry(store, tmp_path):
    code = _run(store.generate_code("telegram", "777", "a@b.cz"))
    path = _pending_file(tmp_path, "telegram", "777")
    wrong = "000000" if code != "000000" else "111111"

    result = _run(store.verify_code("telegram", "777", wrong))
    assert result is None
    # On a wrong code we KEEP the entry so the user can retry.
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["code"] == code


def test_verify_code_returns_none_when_no_pending(store):
    assert _run(store.verify_code("telegram", "no-such-user", "123456")) is None


def test_verify_code_expired_returns_none_and_consumes_entry(store, tmp_path):
    code = _run(store.generate_code("whatsapp", "999", "a@b.cz"))
    path = _pending_file(tmp_path, "whatsapp", "999")

    # Rewind the timestamp so the entry is older than the expiry window.
    record = json.loads(path.read_text(encoding="utf-8"))
    record["created_at"] = time.time() - (15 * 60)
    path.write_text(json.dumps(record), encoding="utf-8")

    result = _run(store.verify_code("whatsapp", "999", code, expiry_minutes=10))
    assert result is None
    assert not path.exists()


def test_verify_code_strips_whitespace(store):
    code = _run(store.generate_code("telegram", "777", "a@b.cz"))
    assert _run(store.verify_code("telegram", "777", f"  {code}  ")) == "a@b.cz"


def test_two_store_instances_share_pending_codes_via_disk(tmp_path):
    """The whole point of the change: a code written by one process / replica
    is readable by another instance pointing at the same data dir."""
    s1 = UserStore(tmp_path / "users.json")
    s2 = UserStore(tmp_path / "users.json")

    code = _run(s1.generate_code("whatsapp", "420111", "a@b.cz"))
    # s2 has no in-memory state; reads from the same disk.
    assert _run(s2.verify_code("whatsapp", "420111", code)) == "a@b.cz"
    # The consume happens on disk — s1 also sees it gone.
    assert _run(s1.verify_code("whatsapp", "420111", code)) is None


def test_concurrent_users_do_not_share_a_file(store, tmp_path):
    """File-per-user is what protects two replicas writing different users
    from clobbering each other. Pin that they're stored separately."""
    a = _run(store.generate_code("telegram", "111", "a@b.cz"))
    b = _run(store.generate_code("telegram", "222", "x@y.cz"))

    path_a = _pending_file(tmp_path, "telegram", "111")
    path_b = _pending_file(tmp_path, "telegram", "222")
    assert path_a.exists() and path_b.exists()
    assert path_a != path_b

    assert _run(store.verify_code("telegram", "111", b)) is None
    assert _run(store.verify_code("telegram", "222", a)) is None
    assert _run(store.verify_code("telegram", "111", a)) == "a@b.cz"
    assert _run(store.verify_code("telegram", "222", b)) == "x@y.cz"


def test_missing_directory_handled_cleanly(tmp_path):
    """A fresh data dir has no pending_codes/ directory yet."""
    store = UserStore(tmp_path / "users.json")
    assert not (tmp_path / "pending_codes").exists()
    assert _run(store.verify_code("telegram", "999", "123456")) is None


def test_corrupt_record_treated_as_missing_and_cleaned_up(store, tmp_path):
    """Garbage JSON in a per-user file should not crash verify; the bad file
    should be cleaned up so it doesn't pollute the directory."""
    path = _pending_file(tmp_path, "telegram", "777")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ this is not json", encoding="utf-8")

    assert _run(store.verify_code("telegram", "777", "123456")) is None
    assert not path.exists()


@pytest.mark.parametrize("bad_record", [
    {"email": "a@b.cz", "code": "123456", "created_at": None},   # null timestamp
    {"email": "a@b.cz", "code": "123456", "created_at": "soon"}, # non-numeric timestamp
    {"email": "a@b.cz", "code": "", "created_at": time.time()},  # empty code
    {"email": "", "code": "123456", "created_at": time.time()},  # empty email
    {"email": None, "code": "123456", "created_at": time.time()},# null email
    {"code": "123456", "created_at": time.time()},               # missing email
    {"email": "a@b.cz", "created_at": time.time()},              # missing code
    "not a dict",                                                # wrong top-level type
])
def test_malformed_record_returns_none(store, tmp_path, bad_record):
    """Defensive: malformed records on disk must not crash verify."""
    path = _pending_file(tmp_path, "telegram", "777")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bad_record), encoding="utf-8")
    assert _run(store.verify_code("telegram", "777", "123456")) is None


def test_unsafe_chars_in_channel_id_dont_break_filename(tmp_path):
    """channel_id is alphanumeric in practice (phone numbers, telegram int IDs),
    but defensive sanitization should let weird inputs through without crashing
    or escaping the pending_codes/ directory."""
    store = UserStore(tmp_path / "users.json")
    # path traversal attempt
    code = _run(store.generate_code("whatsapp", "../escape", "a@b.cz"))
    assert _run(store.verify_code("whatsapp", "../escape", code)) == "a@b.cz"
    # Confirm nothing was written outside the pending_codes directory
    pending_files = list((tmp_path / "pending_codes").iterdir())
    assert len(pending_files) == 0  # consumed
