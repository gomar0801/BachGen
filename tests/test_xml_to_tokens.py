import pytest
from bachgen.score_to_tokens import MusicXML_to_tokens

def test_minimal_xml_to_tokens():
    """Test converting minimal MusicXML to tokens"""
    tokens = MusicXML_to_tokens('musicxml_sample/minimal.musicxml')
    expected = ['R', 'bar', 'clef_treble', 'key_natural_0', 'time_4/4', 'note_C4', 'len_4', 'L', 'bar']
    assert tokens == expected

def test_xml_to_tokens_with_note_numbers():
    """Test converting MusicXML to tokens with MIDI note numbers"""
    tokens = MusicXML_to_tokens('musicxml_sample/minimal.musicxml', note_name=False)
    expected = ['R', 'bar', 'clef_treble', 'key_natural_0', 'time_4/4', 'note_60', 'len_4', 'L', 'bar']  # C4 = MIDI 60
    assert tokens == expected