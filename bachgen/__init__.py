from music21 import environment
import os

for p in ['/Applications/MuseScore 4.app/Contents/MacOS/mscore', 
          '/Applications/MuseScore 3.app/Contents/MacOS/mscore', 
          '/usr/bin/mscore']:
    if os.path.exists(p):
        us = environment.UserSettings()
        us['musescoreDirectPNGPath'] = p
        us['musicxmlPath'] = p
        break