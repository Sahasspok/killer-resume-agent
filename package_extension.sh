#!/usr/bin/env bash
set -e

# Package Killer Resume Agent for Chrome Web Store / Browser Extensions
# Ensures manifest.json is at the exact root level of the ZIP archive.

OUTPUT_ZIP="killer-resume-extension.zip"
rm -f "$OUTPUT_ZIP"

echo "Packaging Chrome Extension with manifest.json at the root..."
zip -r "$OUTPUT_ZIP" manifest.json icons web icon16.png icon48.png icon128.png -x "*.DS_Store*" -x "*__pycache__*"

echo "Successfully created $OUTPUT_ZIP ready for Chrome Web Store upload!"
