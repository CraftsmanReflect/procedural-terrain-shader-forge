"""PluginRegistry — name -> class maps for generators and shader stages."""
from __future__ import annotations

import logging
from typing import Type

from contracts.generator import TerrainGenerator
from contracts.shader import ShaderStage

_LOG = logging.getLogger(__name__)


class PluginRegistry:
    def __init__(self) -> None:
        self._generators: dict[str, Type[TerrainGenerator]] = {}
        self._shader_stages: dict[str, Type[ShaderStage]] = {}

    def add_generator(self, name: str, cls: Type[TerrainGenerator]) -> None:
        if name in self._generators:
            _LOG.warning("generator name collision: %s (overwriting)", name)
        self._generators[name] = cls

    def add_shader_stage(self, name: str, cls: Type[ShaderStage]) -> None:
        if name in self._shader_stages:
            _LOG.warning("shader stage name collision: %s (overwriting)", name)
        self._shader_stages[name] = cls

    def get_generator(self, name: str) -> TerrainGenerator:
        try:
            return self._generators[name]()
        except KeyError as exc:
            raise KeyError(f"no generator plugin named {name!r}") from exc

    def get_shader_stage(self, name: str) -> ShaderStage:
        try:
            return self._shader_stages[name]()
        except KeyError as exc:
            raise KeyError(f"no shader stage named {name!r}") from exc

    def generators(self) -> list[str]:
        return sorted(self._generators)

    def shader_stages(self) -> list[str]:
        return sorted(self._shader_stages)