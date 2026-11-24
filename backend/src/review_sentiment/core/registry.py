"""
Generic plugin registry - the backbone of the Open/Closed Principle in this project.

Datasets, encoders, classifiers and metrics are all looked up *by name* in a registry.
To add a new one you write a new module and decorate it with ``@registry.register("name")``;
no existing code has to be modified.

``import_submodules`` imports every module of a package, so a new plugin file is
discovered automatically just by being placed in the right folder.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable, Iterator


class Registry[T]:
    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._items: dict[str, T] = {}

    def register(self, name: str) -> Callable[[T], T]:
        """Decorator: ``@registry.register("logistic-regression")``."""

        def decorator(item: T) -> T:
            if name in self._items:
                raise ValueError(f"{self._kind} '{name}' is already registered")
            self._items[name] = item
            return item

        return decorator

    def get(self, name: str) -> T:
        try:
            return self._items[name]
        except KeyError:
            available = ", ".join(sorted(self._items)) or "none"
            raise KeyError(f"Unknown {self._kind} '{name}'. Available: {available}") from None

    def names(self) -> list[str]:
        """Registered names, in registration order."""
        return list(self._items)

    def __contains__(self, name: object) -> bool:
        return name in self._items

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())

    def __repr__(self) -> str:
        return f"Registry({self._kind!r}, {self.names()})"


def import_submodules(package_name: str) -> None:
    """Import all modules of a package so their ``@register`` decorators run."""
    package = importlib.import_module(package_name)
    for module in pkgutil.iter_modules(package.__path__):
        if not module.name.startswith("_"):
            importlib.import_module(f"{package_name}.{module.name}")
