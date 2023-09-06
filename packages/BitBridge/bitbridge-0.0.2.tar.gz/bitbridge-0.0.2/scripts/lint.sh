#!/bin/bash -e

PACKAGE_PATH="bitbridge"

ruff "$PACKAGE_PATH" tests
black "$PACKAGE_PATH" tests --check