import pytest
from bachgen.score_to_tokens import MusicXML_to_tokens

def test_minimal_xml_to_tokens():
    """Test converting minimal MusicXML to tokens"""
    tokens = MusicXML_to_tokens('musicxml_sample/minimal.musicxml')
    expected = ['R', 'bar', 'clef_treble', 'key_natural_0', 'time_4/4', 'note_C4', 'len_4', 'L', 'bar']
    assert tokens == expected
'''
def test_xml_to_tokens_with_note_numbers():
    """Test converting MusicXML to tokens with MIDI note numbers"""
    tokens = MusicXML_to_tokens('musicxml_sample/minimal.musicxml', note_name=False)
    expected = ['R', 'bar', 'clef_treble', 'key_natural_0', 'time_4/4', 'note_60', 'len_4', 'L', 'bar']  # C4 = MIDI 60
    assert tokens == expected
'''

def test_sample1_xml_to_tokens():
    """Test MusicXML avec une main droite simple et une main gauche vide (mais avec attributs)"""
    tokens = MusicXML_to_tokens('musicxml_sample/sample1.musicxml')
    expected = [
        'R', 'bar', 'key_natural_0', 'time_4/4', 'clef_treble',
        'note_C4', 'len_1',
        'note_D4', 'len_1',
        'note_E4', 'len_1',
        'note_F4', 'len_1',
        'L', 'bar', 'key_natural_0', 'time_4/4', 'clef_bass'
    ]
    assert tokens == expected

def test_note_transparente_sans_voice_xml_to_tokens():
    """Test MusicXML avec une main droite simple et une main gauche vide (mais avec attributs)"""
    tokens = MusicXML_to_tokens('musicxml_sample/note_transparente_sans_voice.musicxml')
    expected = [
        'R', 'bar', 'key_natural_0', 'time_4/4', 'clef_treble',
        'note_C4', 'len_1',
        'note_D4', 'len_1',
        'note_E4', 'len_1',
        'note_F4', 'len_1',
        'L', 'bar', 'key_natural_0', 'time_4/4', 'clef_bass'
    ]
    assert tokens == expected

def test_note_transparente_avec_voice_xml_to_tokens():
    """Test MusicXML avec une main droite simple et une main gauche vide (mais avec attributs)"""
    tokens = MusicXML_to_tokens('musicxml_sample/note_transparente_avec_voice.musicxml')
    expected = [
        'R', 'bar', 'key_natural_0', 'time_4/4', 'clef_treble',
        'note_C4', 'len_1',
        'note_D4', 'len_1',
        'note_E4', 'len_1',
        'note_F4', 'len_1',
        'L', 'bar', 'key_natural_0', 'time_4/4', 'clef_bass'
    ]
    assert tokens == expected

def test_chord_sans_voice_xml_to_tokens():
    """Test MusicXML avec une main droite simple et une main gauche vide (mais avec attributs)"""
    tokens = MusicXML_to_tokens('musicxml_sample/chord_sans_voice.musicxml')
    expected = [
        'R', 'bar', 'key_natural_0', 'time_4/4', 'clef_treble',
        'note_E4', 'note_C4', 'len_1',
        'note_F4', 'note_D4', 'len_1',
        'note_G4', 'note_E4', 'len_1',
        'note_A4', 'note_F4', 'len_1',
        'L', 'bar', 'key_natural_0', 'time_4/4', 'clef_bass'
    ]
    assert tokens == expected

def test_chord_meme_voice_xml_to_tokens():
    """Test MusicXML avec une main droite simple et une main gauche vide (mais avec attributs)"""
    tokens = MusicXML_to_tokens('musicxml_sample/chord_meme_voice.musicxml')
    expected = [
        'R', 'bar', 'key_natural_0', 'time_4/4', 'clef_treble',
        'note_E4', 'note_C4', 'len_1',
        'note_F4', 'note_D4', 'len_1',
        'note_G4', 'note_E4', 'len_1',
        'note_A4', 'note_F4', 'len_1',
        'L', 'bar', 'key_natural_0', 'time_4/4', 'clef_bass'
    ]
    assert tokens == expected

def test_chord_2voice_xml_to_tokens():
    """Test MusicXML avec une main droite simple et une main gauche vide (mais avec attributs)"""
    tokens = MusicXML_to_tokens('musicxml_sample/chord_2voice_(backup).musicxml')
    expected = [
        'R', 'bar', 'key_natural_0', 'time_4/4', 'clef_treble',
        'note_C5', 'note_C4', 'len_1',
        'note_D5', 'note_D4', 'len_1',
        'note_E5', 'note_E4', 'len_1',
        'note_F5', 'note_F4', 'len_1',
        'L', 'bar', 'key_natural_0', 'time_4/4', 'clef_bass'
    ]
    assert tokens == expected

def test_chevauchement_xml_to_tokens():
    """Test MusicXML avec une main droite simple et une main gauche vide (mais avec attributs)"""
    tokens = MusicXML_to_tokens('musicxml_sample/chevauchement.musicxml')
    expected = [
        'R', 'bar', 'key_natural_0', 'time_4/4', 'clef_treble',
        'note_C5', 'note_C4', 'len_1',
        'note_D5', 'len_1',
        'note_E5', 'note_E4', 'len_1',
        'note_F5', 'note_F4', 'len_1',
        'L', 'bar', 'key_natural_0', 'time_4/4', 'clef_bass'
    ]
    assert tokens == expected
