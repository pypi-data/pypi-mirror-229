from __future__ import annotations

import sys
from configparser import ConfigParser, _UNSET
from pathlib import Path

from .logging import _get_prog


def get_config(prog: str) -> ExtendedConfigParser:
    """
    A function to search for configuration files in some common paths.
    """
    if not prog:
        raise ValueError("prog required")
        # NOTE: we should not try to determine prog here: this is too dangerous (invalid/fake configuration files could be loaded by mistake)

    parser = ExtendedConfigParser()

    parser.read([
        # System configuration
        Path(f'C:/ProgramData/{prog}.conf' if sys.platform == 'win32' else f'/etc/{prog}.conf').expanduser(),
        # User configuration
        Path(f'~/.config/{prog}.conf').expanduser(),
        # Local configuration
        "local.conf",
    ], encoding='utf-8')

    return parser


class ExtendedConfigParser(ConfigParser):
    def getlist(self, section: str, option: str, *, fallback: list[str]|None = _UNSET, separator: str = ',') -> list[str]:
        try:            
            values_str = self.get(section, option)
        except:
            if fallback != _UNSET:
                return fallback
            raise

        values = []
        for value in values_str.split(separator):
            value = value.strip()
            if not value:
                continue
            values.append(value)

        return values
