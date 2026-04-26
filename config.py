"""Configuration loader — reads config.yaml with env var interpolation."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass
class TelegramConfig:
    rulemaster_token: str
    loremaster_token: str


@dataclass
class WahaConfig:
    url: str
    api_key: str = ""
    session: str = "default"


@dataclass
class AnthropicConfig:
    api_key: str
    model: str = "claude-sonnet-4-6"


@dataclass
class RegistraceConfig:
    api_url: str
    api_key: str
    integration_api_key: str
    game_id: str


@dataclass
class AzureEmailConfig:
    connection_string: str
    sender_address: str


@dataclass
class AuthConfig:
    code_expiry_minutes: int = 10
    organizer_emails: list[str] = field(default_factory=list)
    fate_emails: list[str] = field(default_factory=list)


@dataclass
class HraConfig:
    api_url: str
    api_token: str
    game_id: int = 30


@dataclass
class BacaConfig:
    api_url: str
    api_key: str


@dataclass
class ConversationConfig:
    max_history: int = 20


@dataclass
class LoreMasterConfig:
    brain_path: Path
    kb_public_path: Path
    game_path: Path = None


@dataclass
class Config:
    telegram: TelegramConfig
    waha: WahaConfig
    anthropic: AnthropicConfig
    registrace: RegistraceConfig
    azure_email: AzureEmailConfig
    skills_path: Path
    pravidla_path: Path
    loremaster: LoreMasterConfig
    hra: HraConfig
    baca: BacaConfig
    auth: AuthConfig
    conversation: ConversationConfig
    rule_editors: list[str] = field(default_factory=list)


_ENV_PATTERN = re.compile(r"\$\{(\w+)\}")


def _resolve_env(value: str) -> str:
    """Replace ${VAR} with environment variable value."""
    def replacer(match: re.Match) -> str:
        var = match.group(1)
        env_val = os.environ.get(var)
        if env_val is None:
            raise ValueError(f"Environment variable {var} not set")
        return env_val

    if isinstance(value, str):
        return _ENV_PATTERN.sub(replacer, value)
    return value


def _resolve_dict(d: dict) -> dict:
    """Recursively resolve env vars in a dict."""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _resolve_dict(v)
        elif isinstance(v, str):
            result[k] = _resolve_env(v)
        elif isinstance(v, list):
            result[k] = [_resolve_env(i) if isinstance(i, str) else i for i in v]
        else:
            result[k] = v
    return result


def load_config(path: str = "config.yaml") -> Config:
    """Load and validate configuration."""
    load_dotenv()

    config_path = Path(__file__).parent / path
    if not config_path.exists():
        raise FileNotFoundError(
            f"{config_path} not found. Copy config.example.yaml to config.yaml and fill in values."
        )

    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    resolved = _resolve_dict(raw)

    return Config(
        telegram=TelegramConfig(**resolved["telegram"]),
        waha=WahaConfig(**resolved["waha"]),
        anthropic=AnthropicConfig(**resolved["anthropic"]),
        registrace=RegistraceConfig(**resolved["registrace"]),
        azure_email=AzureEmailConfig(**resolved["azure_email"]),
        skills_path=Path(resolved["skills_path"]),
        pravidla_path=Path(resolved["pravidla"]["path"]),
        rule_editors=resolved["pravidla"].get("editors", []),
        loremaster=LoreMasterConfig(
            brain_path=Path(resolved["loremaster"]["brain_path"]),
            kb_public_path=Path(resolved["loremaster"]["kb_public_path"]),
            game_path=Path(resolved["loremaster"]["game_path"]) if resolved["loremaster"].get("game_path") else None,
        ),
        hra=HraConfig(**resolved["hra"]),
        baca=BacaConfig(**resolved["baca"]),
        auth=AuthConfig(**resolved.get("auth", {})),
        conversation=ConversationConfig(**resolved.get("conversation", {})),
    )
