# Development

**SR CADLib** is a Python library for agents driving Fusion. Work on a branch and open a PR against `main`.

## Clone

```
git clone https://github.com/living-relation/sr-cadlib.git
```

## Layout

| Path | Role |
| --- | --- |
| `sr_cadlib/` | Package: `config.py`, `registry.py`, `fusion.py` |
| `examples/build_example.py` | Copy-paste agent sample |
| `dev/fusion_smoke.py` | Live Fusion smoke test (closes without saving) |
| `tests/` | Unit tests; Fusion is mocked |
| `tools/check.py` | CI entry: tests, no secrets, no machine paths, no forbidden project names |

## Checks

```
python tools/check.py
```

CI runs the same command. Unit tests do not need Fusion. `tools/check.py` fails if the tree contains a forbidden project name, a machine home path, a secret, or a vendor CAD file.

## Coding notes

- This repository is public. Do not commit secrets, tokens, or machine-specific paths.
- Keep the library generic. Do not add product or project names to the library, docs, examples, tests, or commit messages.
- Docs are for AI agents (Fusion MCP / script runner), not for people writing scripts by hand.
- Live Fusion tests: take the machine Fusion lock first, and never touch other open documents. `dev/fusion_smoke.py` closes its own design without saving.

## Contributing

1. Branch from `main`.
2. Update `docs/` when behavior changes.
3. Run `python tools/check.py`.
4. Open a pull request against `main`.
