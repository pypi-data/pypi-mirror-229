# spdx-license-identifier: gpl-3.0-only
# Copyright (C) 2022 Michał Góral

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version("ntfy-send")
