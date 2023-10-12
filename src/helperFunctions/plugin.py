from __future__ import annotations

import logging
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path

from helperFunctions.fileSystem import get_src_dir
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType
    from importlib.machinery import ModuleSpec


def discover_analysis_plugins() -> list[ModuleType]:
    """Returns a list of modules where each module is an analysis plugin."""
    return _import_plugins('analysis')


def discover_compare_plugins() -> list[ModuleType]:
    """Returns a list of modules where each module is a compare plugin."""
    return _import_plugins('compare')


def _import_plugins(plugin_type) -> list[ModuleType]:
    assert plugin_type in ['analysis', 'compare']

    plugins = []
    src_dir = get_src_dir()
    for plugin_file in Path(src_dir).glob(f'plugins/{plugin_type}/*/code/*.py'):
        if plugin_file.name == '__init__.py':
            continue

        # The module name has to be the name in the FACT import tree.
        # If it isn't we can't do relative imports of the `internal` modules
        module_name = str(plugin_file).replace('/', '.')[len(src_dir + '/') : -len('.py')]

        loader = SourceFileLoader(module_name, str(plugin_file))
        spec: ModuleSpec = spec_from_loader(loader.name, loader)  # type: ignore[assignment]
        plugin_module = module_from_spec(spec)

        sys.modules[spec.name] = plugin_module
        try:
            loader.exec_module(plugin_module)
            plugins.append(plugin_module)
        except Exception:
            sys.modules.pop(spec.name)
            # This exception could be caused by upgrading dependencies to incompatible versions. Another cause could
            # be missing dependencies. So if anything goes wrong we want to inform the user about it
            logging.error(f'Could not import plugin {module_name} due to exception', exc_info=True)

    return plugins
