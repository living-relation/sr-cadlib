# Agent rules for sr-cadlib

- This repo is **public**. Never commit secrets, tokens, personal or machine paths, or vendor CAD
  files (STEP, f3d, SLDPRT, and the like). `tools/check.py` scans for these.
- Keep the library generic. Do not add customer, product or machine-specific names or paths.
  Callers pass those in through `configure()`. `tools/check.py` fails the build if a forbidden
  project name appears in the tree.
- Work on a branch and open a PR. Never commit to `main`. Delete the branch once it is merged.
- Run `python tools/check.py` before every push. CI runs the same check.
- This is an agent helper library, not a Fusion add-in and not for humans writing scripts by hand.
  Docs are written for AI agents driving Fusion (Fusion MCP / script runner). Scripts import it after `pip install -e .` or
  by putting this repository on `PYTHONPATH`. See [docs/install.md](docs/install.md).
- Do not write assembly instructions such as tightening torque or threadlocker notes.
- Live Fusion tests: take the machine's Fusion lock first, and never touch other people's open
  documents. The smoke test in `dev/fusion_smoke.py` closes its own design without saving.
