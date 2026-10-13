"""TerrainGenerator — the contract every generator plugin implements."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from models.terrain import HeightField, TileSpec


class TerrainGenerator(ABC):
    """Produces a HeightField for a given TileSpec.

    Implementations MUST be pure with respect to `params`: same spec + same
    params -> identical heightfield (seeded RNG only). This is what makes
    bake caching and golden-hash tests work.
    """

    #: Declared by the plugin module; the loader reads PLUGIN_META, not this.
    name: str = "unnamed"

    @abstractmethod
    def generate(self, tile: TileSpec, params: dict[str, Any]) -> HeightField:
        """Return a HeightField of shape (tile.resolution, tile.resolution).

        Raises:
            ValueError: if params fail the plugin's own schema check.
        """

    def param_schema(self) -> dict[str, Any]:
        """Optional JSON-schema-ish description used by the CLI param parser."""
        return {}