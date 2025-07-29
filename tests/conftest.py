import pytest
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture
def sample_tokens():
    """Fixture providing minimal token sequence"""
    return "R bar clef_treble key_natural_0 time_4/4 note_C4 len_4 L bar"

@pytest.fixture
def sample_xml_path():
    """Fixture providing path to minimal MusicXML file"""
    return "musicxml_sample/minimal.musicxml"