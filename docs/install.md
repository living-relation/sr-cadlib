# Install

SR CADLib is a library, not a Fusion add-in. Do not add it in the Scripts and Add-Ins dialog. An agent loads it from a Fusion MCP `execute_python` script (or the script runner) after the repo is on the Python path.

## Requirements

- Autodesk Fusion
- A local clone of this repository

## Put the library on the path

Clone the repo onto the machine that runs Fusion:

```
git clone https://github.com/living-relation/sr-cadlib.git
```

Then, in the script the agent sends to Fusion, insert the clone root before importing:

```python
import sys
sys.path.insert(0, "/path/to/sr-cadlib")  # replace with the local clone path
import sr_cadlib as cad
```

Optional, for a persistent install in that machine's Python:

```
pip install -e /path/to/sr-cadlib
```

Confirm:

```python
import sr_cadlib as cad
print(cad.MM, cad.IN)
```

`MM` and `IN` work without Fusion. Calls that build or save geometry need Fusion to be running.

## Uninstall

Remove the clone from `sys.path` (or uninstall the editable package) and delete the local clone if it is no longer needed.

## Next

[Usage](usage.md)
