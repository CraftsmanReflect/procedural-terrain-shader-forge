"""TerrainForgeHost — owns the registry, event bus, loader, and preview loop."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from forge_host.event_bus import EventBus
from forge_host.loader import PluginLoader
from forge_host.registry import PluginRegistry
from models.terrain import TileSpec
from utils.config import ForgeConfig

_LOG = logging.getLogger(__name__)


@dataclass
class TerrainForgeHost:
    """The plugin host. Composition root for the whole tool.

    Owns:
      - PluginRegistry: name -> plugin instance
      - EventBus: pub/sub for tile lifecycle + shader reload events
      - PluginLoader: filesystem discovery + import

    Concurrency: single-threaded control plane. The bake service runs its
    own worker pool; the host only touches the GPU on the main thread.
    """

    config: ForgeConfig
    registry: PluginRegistry = field(init=False)
    bus: EventBus = field(init=False)
    loader: PluginLoader = field(init=False)
    _running: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.registry = PluginRegistry()
        self.bus = EventBus()
        self.loader = PluginLoader(
            plugin_dirs=self.config.host.plugin_dirs,
            allow_native=self.config.host.allow_native_plugins,
            registry=self.registry,
            bus=self.bus,
        )

    def start(self) -> None:
        self._running = True
        self.loader.discover_and_load()
        if self.config.host.watch_plugins:
            self.loader.start_watch()
        _LOG.info(
            "host up: %d generators, %d shader stages",
            len(self.registry.generators()),
            len(self.registry.shader_stages()),
        )

    def run_preview(self) -> None:
        from shader_pipeline.preview import PreviewWindow

        win = PreviewWindow(self.config, self.registry, self.bus)
        win.run()

    def wait(self) -> None:
        while self._running:
            time.sleep(0.25)

    def generate_tile(self, spec: TileSpec, generator: str, params: dict[str, Any] | None = None):
        gen = self.registry.get_generator(generator)
        self.bus.publish("tile.begin", spec=spec, generator=generator)
        hf = gen.generate(spec, params or {})
        self.bus.publish("tile.done", spec=spec, heightfield=hf)
        return hf

    def stop(self) -> None:
        self._running = False
        self.loader.stop_watch()
        _LOG.info("host down")