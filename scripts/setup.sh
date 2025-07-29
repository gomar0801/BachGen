#!/bin/bash

# Install MuseScore
brew install --cask musescore 2>/dev/null || apt-get install -y musescore

# Install the requirements
pip install -r BachGen/requirements.txt
pip install ./BachGen