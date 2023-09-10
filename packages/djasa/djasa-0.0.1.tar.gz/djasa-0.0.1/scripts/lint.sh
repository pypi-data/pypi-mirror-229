#!/bin/bash -e

PACKAGE_PATH="djasa"

ruff "$PACKAGE_PATH" tests
black "$PACKAGE_PATH" tests --check