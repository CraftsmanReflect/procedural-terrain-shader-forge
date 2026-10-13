# Contributing to procedural-terrain-shader-forge

Thanks for wanting to hack on the forge. This is a plugin-host architecture:
the core host loads terrain generator plugins and shader stage plugins at
runtime from the `plugins/` tree. Read the contracts before you write a plugin.

## Repo layout

- `forge_host/` — the core host: bootstrap, event bus, plugin loader, registry
- `terrain_core/` — heightfield, noise, erosion, mesh extraction primitives
- `shader_pipeline/` — GLSL stage compilation, uniform binding, hot-reload
- `plugins/` — first-party generator + shader plugins (drop-in)
- `contracts/` — abstract base classes every plugin must implement
- `services/` — long-running services (bake service, preview service)
- `models/` — dataclasses for terrain params, tiles, meshes
- `utils/` — math, io, profiling helpers
- `config/` — default TOML config + schema
- `tests/` — pytest suite

## Writing a generator plugin

1. Subclass `contracts.generator.TerrainGenerator`.
2. Implement `generate(tile: TileSpec, params: dict) -> HeightField`.
3. Declare `PLUGIN_META` at module top (name, version, params schema).
4. Drop the file in `plugins/generators/` — the loader picks it up on next
   host start, or immediately if `--watch-plugins` is set.

## Writing a shader stage plugin

1. Subclass `contracts.shader.ShaderStage`.
2. Provide `vertex_src` and `fragment_src` (GLSL 4.60 core).
3. Declare required uniforms in `uniform_contract`.
4. Drop in `plugins/shaders/`. Hot-reload watches mtime.

## Style

- Python 3.12+, type hints on every public function.
- `ruff` for lint, `mypy --strict` on `terrain_core/` and `contracts/`.
- No prints in library code — use `logging.getLogger(__name__)`.

## Tests

```
pytest -q
```
New generator plugin? Add a fixture tile in `tests/fixtures/` and a golden
heightmap hash assertion.

## Sign-off

Commits need `Signed-off-by:` (DCO). No CLA.