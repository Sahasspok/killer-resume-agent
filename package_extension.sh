#!/usr/bin/env bash
set -e

# Package Killer Resume Agent for Chrome Web Store / Browser Extensions
# Ensures manifest.json is at the exact root level of the ZIP archive, with no duplicates and no wrapper folder.

OUTPUT_ZIP="killer-resume-extension.zip"
DOWNLOADS_ZIP="$HOME/Downloads/killer-resume-extension.zip"

rm -f "$OUTPUT_ZIP" "$DOWNLOADS_ZIP"

echo "Packaging Chrome Extension with exactly ONE manifest.json at the root..."
zip -r "$OUTPUT_ZIP" manifest.json icons web icon16.png icon48.png icon128.png -x "*.DS_Store*" -x "*__pycache__*"

# Copy to Downloads for easy upload from browser file picker
cp "$OUTPUT_ZIP" "$DOWNLOADS_ZIP"

echo "Successfully created:"
echo "1. $(pwd)/$OUTPUT_ZIP"
echo "2. $DOWNLOADS_ZIP"
