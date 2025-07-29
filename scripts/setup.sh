#!/bin/bash

# Install MuseScore
if command -v brew &> /dev/null; then
    # macOS
    brew install --cask musescore 2>/dev/null
elif command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update && sudo apt-get install -y musescore
fi

# Install Python dependencies
if [ "$GITHUB_ACTIONS" = "true" ]; then
    # In GitHub Actions
    pip install -r requirements.txt
    pip install .
else
    pip install -r BachGen/requirements.txt
    pip install ./BachGen
fi