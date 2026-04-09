#!/usr/bin/env bash
# export.sh — export the codelab and inject the "About this codelab" card
set -euo pipefail
export PATH=$PATH:$(go env GOPATH)/bin

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CODELAB_DIR="$SCRIPT_DIR/ai-creative-studio-adk-a2a"
DOCS_DIR="$SCRIPT_DIR/../docs"

cd "$SCRIPT_DIR"

echo "Exporting codelab..."
claat export codelab.md

echo "Injecting 'About this codelab' card..."
python3 "$SCRIPT_DIR/inject_about.py" "$CODELAB_DIR/index.html"

echo "Copying to docs/..."
mkdir -p "$DOCS_DIR"
cp -r "$CODELAB_DIR/." "$DOCS_DIR/"

echo "Exporting Mete's codelabs version (index.lab.md)..."
claat export index.lab.md
mkdir -p "$DOCS_DIR/codelabs"
cp -r "$CODELAB_DIR/." "$DOCS_DIR/codelabs/"

echo "Done. Workshop: docs/  |  Codelabs: docs/codelabs/"
