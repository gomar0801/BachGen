#!/bin/bash

# Install MuseScore
brew install --cask musescore 2>/dev/null || apt-get install -y musescore

if [ "$GITHUB_ACTIONS" = "true" ]; then
pip install -r requirements.txt
pip install .
else
# Install the requirements
pip install -r BachGen/requirements.txt
pip install ./BachGen
fi