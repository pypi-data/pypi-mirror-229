# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
# @file
# @author Neil Vaytet, Jan-Lukas Wynen
"""
Runtime configuration.

See https://scipp.github.io/reference/runtime-configuration.html
"""

# *** For developers ***
#
# When adding new options, update both the file config_default.yaml
# and Config._TEMPLATE.
# If the template is not updated, new options will simply be ignored.

from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Tuple

import confuse


class Config:
    """
    Runtime configuration parameters.

    Provides dict-like access to configuration parameters.
    Modifications apply to the current process only and do not
    modify any configuration files.

    See https://scipp.github.io/reference/runtime-configuration.html
    """

    _TEMPLATE = {
        'colors': confuse.MappingValues(str),
        'table_max_size': int,
    }

    def __init__(self):
        self._cfg = confuse.LazyConfig('scipp', __name__)

    def config_dir(self) -> Path:
        """
        Return the directory for configuration files.

        The directory is created if it does not already exist.
        """
        return Path(self._cfg.config_dir())

    def config_path(self) -> Path:
        """
        Return the path to the configuration file.

        The file may not exist but its folder is created if it does not already exist.
        """
        return Path(self._cfg.user_config_path())

    def _read(self):
        try:
            self._cfg.read(user=True, defaults=True)
        except PermissionError:
            # On some systems, the user configuration directories are read-only.
            # confuse tries to create a subdirectory for scipp if it does not
            # already exist and that raises PermissionError.
            # Fall back to the default configuration shipped as part of the
            # source code in this case.
            self._cfg.read(user=False, defaults=True)
        # Add source after _cfg.read to override 'user' and 'defaults'
        self._cfg.set(
            confuse.YamlSource(
                './scipp.config.yaml', optional=True, loader=self._cfg.loader
            )
        )

    @lru_cache()  # noqa: B019
    def get(self) -> dict:
        """Return parameters as a dict."""
        self._read()
        return self._cfg.get(self._TEMPLATE)

    def __getitem__(self, name: str):
        """Return parameter of given name."""
        return self.get()[name]

    def __setitem__(self, name: str, value):
        """Change the value of a parameter."""
        if name not in self.get():
            raise TypeError(
                f"New items cannot be inserted into the configuration, got '{name}'."
            )
        self.get()[name] = value

    def keys(self) -> Iterable[str]:
        """Returns iterable over parameter names."""
        yield from self.get().keys()

    def values(self) -> Iterable[Any]:
        """Returns iterable over parameter values."""
        yield from self.get().values()

    def items(self) -> Iterable[Tuple[str, Any]]:
        """Returns iterable over parameter names and values."""
        yield from self.get().items()


config = Config()
__all__ = ['config']
