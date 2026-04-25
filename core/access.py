"""Access control — tag-based lore visibility."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a markdown file.

    Returns (metadata_dict, body_text). If no frontmatter found,
    returns ({}, full_content).
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, match.group(2)


def can_access(meta: dict, user: dict) -> bool:
    """Check if a user can access a lore file based on its přístup metadata.

    Access is additive — returns True if ANY condition matches:
    - veřejné is True → everyone
    - user's frakce is in the frakce list
    - user's postava is in the postavy list
    - user's role is 'organizátor' or 'gm' → sees everything
    """
    pristup = meta.get("přístup", {})

    # No access metadata = public by default (backwards compat for untagged files)
    if not pristup:
        return True

    # GM/organizer sees everything
    if user.get("role") in ("organizátor", "gm"):
        return True

    # Public content
    if pristup.get("veřejné", pristup.get("verejne", False)):
        return True

    # Faction match
    user_frakce = user.get("frakce", "")
    if user_frakce and user_frakce.lower() in [f.lower() for f in pristup.get("frakce", [])]:
        return True

    # Character match
    user_postava = user.get("postava", "")
    if user_postava and user_postava.lower() in [p.lower() for p in pristup.get("postavy", [])]:
        return True

    return False


def load_roles(roles_path: Path) -> dict:
    """Load role profiles from brain/_roles.yaml.

    Returns dict of role_name -> role_data.
    """
    if not roles_path.exists():
        return {}
    with open(roles_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("roles", {})
