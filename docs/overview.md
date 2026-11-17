# Overview

SR CADLib is a Spark Robotic helper library for AI agents driving Autodesk Fusion. An agent imports it from a Fusion MCP `execute_python` call (or the script runner), configures the Fusion project and folders, then builds, saves, and reopens parts without repeating low-level Fusion API boilerplate.

It is generic: callers pass the project name, folder root, registry path, and log path into `configure()`. The library has no built-in product or machine paths.

## Features

- Temporary solids, sketches, extrudes, holes, and combines
- Materials and appearances
- Placement matrices and occurrence insert
- Save to Fusion data folders with part number and description
- A local JSON registry of part key → Fusion file id

## Requirements

- Autodesk Fusion (the `adsk` module), when building or saving
- This repository on `sys.path` or installed with `pip install -e .`
- Python 3.10+ for unit tests (`pytest`). Tests mock `adsk` and do not need Fusion.

## Status

The library lives in the `sr_cadlib` package. Agents should start with the [README](../README.md) quick start and [Usage](usage.md).

## Further reading

- [Install](install.md)
- [Usage](usage.md)
- [Development](development.md)
