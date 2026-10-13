# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security-only |
| < 0.5   | no        |

## Reporting a vulnerability

Terrain shader forge runs untrusted plugin code by design — that is the
whole point of a plugin host. If you find a sandbox escape in
`forge_host/loader.py`, a shader compiler memory bug reachable from GLSL
source, or a path traversal in the bake service, report it privately.

Email: security@procedural-terrain-shader-forge.dev
PGP: `0x9F3A 2C11 88D4 6B7E`

Please include:
- forge version (`forge --version`)
- GPU + driver version
- minimal plugin or `.ptf` repro
- whether the host was started with `--allow-native-plugins`

We triage within 72h. Credit in the release notes unless you ask otherwise.

## Threat model

- Plugins are **not** sandboxed by default. `--allow-native-plugins` is
  required for any plugin that ships a compiled `.pyd`/`.so`; pure-Python
  plugins run in-process with full host privileges.
- Shader source from a plugin is compiled by the system GLSL compiler.
  A malicious shader can hang or crash the GPU driver — run the preview
  service on a throwaway user account if you load third-party shaders.
- `.ptf` bake files are pickle-free (msgpack + raw float32 blobs) but
  still validate tile dimensions before allocating.

## Out of scope

- DoS via absurd terrain resolution (documented limit: 8192x8192 per tile).
- Anything requiring local admin on the user's own machine.