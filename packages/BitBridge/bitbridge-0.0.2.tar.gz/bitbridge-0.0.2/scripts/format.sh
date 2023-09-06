#!/bin/bash -e

PACKAGE_PATH="bitbridge"

ruff "$PACKAGE_PATH" tests --fix
black "$PACKAGE_PATH" tests