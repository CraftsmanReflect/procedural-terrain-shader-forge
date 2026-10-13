"""Filesystem plugin discovery + import. Pure-Python and native (.pyd/.so)."""
from __future__ import annotations

import importlib.util
import logging
import sys
import threading
import time
from pathlib import Path
from types import ModuleType

from contracts.generator import TerrainGenerator
from contracts.shader import ShaderStage
from forge_host.event_bus import EventBus
from forge_host.registry import PluginRegistry

_LOG = logging.getLogger(__name__)

_NATIVE_SUFFIXES = {".pyd", ".so", ".dylib"}


class PluginLoader:
    """Discovers plugins in configured directories and registers them.

    Watch mode polls mtime every `poll_interval_s` and reloads changed
    modules. Reload is best-effort: a plugin whose import raises is logged
    and skipped, never crashes the host.
    """

    def __init__(
        self,
        plugin_dirs: list[str],
        allow_native: bool,
        registry: PluginRegistry,
        bus: EventBus,
        poll_interval_s: float = 1.5,
    ) -> None:
        self._dirs = [Path(d) for d in plugin_dirs]
        self._allow_native = allow_native
        self._registry = registry
        self._bus = bus
        self._poll = poll_interval_s
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._mtimes: dict[Path, float] = {}

    def discover_and_load(self) -> None:
        for d in self._dirs:
            if not d.is_dir():
                _LOG.warning("plugin dir missing: %s", d)
                continue
            for path in sorted(d.glob("*.py")):
                self._load_python(path)
            if self._allow_native:
                for path in sorted(p for p in d.iterdir() if p.suffix in _NATIVE_SUFFIXES):
                    self._load_native(path)

    def _load_python(self, path: Path) -> None:
        mod_name = f"forge_plugin_{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(mod_name, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"no loader for {path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
        except Exception:
            _LOG.exception("plugin import failed: %s", path)
            return
        self._register_from_module(module, path)
        self._mtimes[path] = path.stat().st_mtime

    def _load_native(self, path: Path) -> None:
        try:
            spec = importlib.util.spec_from_file_location(f"forge_native_{path.stem}", path)
            if spec is None or spec.loader is None:
                raise ImportError(f"no loader for {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            _LOG.exception("native plugin load failed: %s", path)
            return
        self._register_from_module(module, path)
        self._mtimes[path] = path.stat().st_mtime

    def _register_from_module(self, module: ModuleType, path: Path) -> None:
        meta = getattr(module, "PLUGIN_META", None)
        if not isinstance(meta, dict) or "name" not in meta:
            _LOG.warning("plugin missing PLUGIN_META: %s", path)
            return
        registered = 0
        for attr in vars(module).values():
            if isinstance(attr, type) and issubclass(attr, TerrainGenerator) and attr is not TerrainGenerator:
                self._registry.add_generator(meta["name"], attr)
                registered += 1
            elif isinstance(attr, type) and issubclass(attr, ShaderStage) and attr is not ShaderStage:
                self._registry.add_shader_stage(meta["name"], attr)
                registered += 1
        if registered:
            _LOG.info("loaded plugin %s (%d entries)", meta["name"], registered)
            self._bus.publish("plugin.loaded", name=meta["name"], path=str(path))

    def start_watch(self) -> None:
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._watch_loop, name="plugin-watch", daemon=True)
        self._thread.start()

    def _watch_loop(self) -> None:
        while not self._stop.wait(self._poll):
            self.discover_and_load()

    def stop_watch(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None