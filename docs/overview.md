# Overview

SR CADLib is a Spark Robotic helper library for Autodesk Fusion API scripting. It provides shared building blocks so Fusion scripts and add-ins can create and place geometry without repeating the same low-level API calls.

It is part of the Spark Robotic (SR-) tool set for Fusion. The library is generic: it is not tied to a single product or project.

## What this repository is today

This repository currently holds documentation, a license, and a Python `.gitignore`. The library code has not been added yet. Feature-specific behavior in these docs is marked as to be completed when the code lands.

## Features

- Helpers for primitives, sketches, and extrudes.
- Helpers for materials and placement.
- Helpers for saving designs or components to Fusion data folders.
- A part registry for looking up or recording parts used by scripts.

The exact functions, arguments, and module layout are to be completed when the code lands.

## Requirements

- Autodesk Fusion

No other requirements are documented yet. Runtime dependencies, if any, are to be completed when the code lands.

## Status

The library will be added in a follow-up pull request. Until then, treat this repository as the public home and documentation for **SR CADLib**.

## Further reading

- [Install](install.md)
- [Usage](usage.md)
- [Development](development.md)
