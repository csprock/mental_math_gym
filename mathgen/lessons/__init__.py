"""
Importing this package auto-imports every non-underscore module beneath it,
which causes each module's ``@register_lesson`` decorators to fire and
populate the global ``LessonRegistry``.
"""
from __future__ import annotations

import importlib
import pkgutil

for _module_info in pkgutil.iter_modules(__path__):
    if _module_info.name.startswith("_"):
        continue
    importlib.import_module(f"{__name__}.{_module_info.name}")
