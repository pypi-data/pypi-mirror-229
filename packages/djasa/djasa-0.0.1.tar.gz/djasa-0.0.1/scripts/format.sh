#!/bin/bash -e

PACKAGE_PATH="djasa"

ruff "$PACKAGE_PATH" tests --fix
black "$PACKAGE_PATH" tests