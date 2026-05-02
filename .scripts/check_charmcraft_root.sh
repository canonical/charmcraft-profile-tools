#!/bin/sh

if [ -z "$CHARMCRAFT_DIR" ]; then
    echo "CHARMCRAFT_DIR is not set" >&2
    exit 1
fi
if ! test -f "$CHARMCRAFT_DIR/pyproject.toml"; then
    echo "No Charmcraft source located at $CHARMCRAFT_DIR" >&2
    exit 1
fi
if ! test -d "$CHARMCRAFT_DIR/charmcraft"; then
    echo "No Charmcraft source located at $CHARMCRAFT_DIR" >&2
    exit 1
fi
