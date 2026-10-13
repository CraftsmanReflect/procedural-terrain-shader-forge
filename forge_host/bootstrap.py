"""Entry point: parse args, load config, spin up the plugin host, run the loop."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from forge_host.host import TerrainForgeHost
from utils.config import load_config

_LOG = logging.getLogger("forge")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="forge",
        description="Procedural terrain generator with shaders (plugin host).",
    )
    p.add_argument("--config", type=Path, default=None, help="path to forge.toml")
    p.add_argument("--plugin-dir", action="append", default=[], help="extra plugin dir")
    p.add_argument("--watch-plugins", action="store_true", help="hot-reload plugins on mtime")
    p.add_argument("--allow-native-plugins", action="store_true", help="permit .pyd/.so plugins")
    p.add_argument("--no-preview", action="store_true", help="headless: skip GL window")
    p.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"])
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    cfg = load_config(args.config)
    if args.plugin_dir:
        cfg.host.plugin_dirs.extend(args.plugin_dir)
    if args.watch_plugins:
        cfg.host.watch_plugins = True
    if args.allow_native_plugins:
        cfg.host.allow_native_plugins = True

    host = TerrainForgeHost(cfg)
    try:
        host.start()
        if args.no_preview:
            _LOG.info("headless mode: host running, ctrl-c to stop")
            host.wait()
        else:
            host.run_preview()
    except KeyboardInterrupt:
        _LOG.info("shutdown requested")
    finally:
        host.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())