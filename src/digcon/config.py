"""Load config/*.yaml into a validated ConfigBundle. The only runtime reader of the spec."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from digcon.domain.models import ConfigBundle

DEFAULT_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
_FILES = ("questions", "rules", "risks", "mitigations", "sep")


class ConfigError(Exception):
    pass


def load_config(config_dir: Path = DEFAULT_CONFIG_DIR) -> ConfigBundle:
    version = (config_dir / "VERSION").read_text(encoding="utf-8").strip()
    data: dict[str, object] = {"version": version}
    for name in _FILES:
        with open(config_dir / f"{name}.yaml", encoding="utf-8") as fh:
            data[name] = yaml.safe_load(fh)
    bundle = ConfigBundle.model_validate(data)
    metas = {name: getattr(bundle, name).meta for name in _FILES}
    if {m.workbook_version for m in metas.values()} != {version}:
        raise ConfigError(f"config files disagree with VERSION {version}: {metas}")
    if len({m.workbook_sha256 for m in metas.values()}) != 1:
        raise ConfigError("config files were generated from different workbooks")
    return bundle


@lru_cache(maxsize=1)
def default_config() -> ConfigBundle:
    return load_config()
