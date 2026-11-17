# Install

This page describes a generic install for a Fusion API helper library. The exact package name, import path, and any extra install steps are to be completed when the code lands.

## Requirements

- Autodesk Fusion
- This repository, cloned or downloaded to a folder you can keep on disk

## Add the library

1. Clone or download this repository:

```
git clone https://github.com/living-relation/sr-cadlib.git
```

2. Make the library available to the Fusion Python scripts or add-ins that will use it. How that is done — for example as a package, a folder on the script path, or a copy next to a script — is to be completed when the code lands.

3. Confirm the library can be imported from a Fusion script. The import statement and a minimal check are to be completed when the code lands.

SR CADLib is a library, not a standalone Fusion add-in or script, so it is not added through the Scripts and Add-Ins dialog on its own. Scripts or add-ins that depend on it are installed in that dialog in the usual way.

## Uninstall

Remove the library from the path or location used in the steps above, then remove any local clone you no longer need. Details are to be completed when the code lands.

## Next

See [Usage](usage.md) after the library is available to your scripts.
