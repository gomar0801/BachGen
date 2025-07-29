"""
MIDI BPE Token Style Pipeline

This package provides utilities for converting between MusicXML, MIDI, and BPE tokens
using pretrained REMI tokenizers.

Main functions:
- music_xml_to_midi: Convert MusicXML files to MIDI
- midi_to_music_xml: Convert MIDI files to MusicXML  
- midi_to_token: Convert MIDI files to BPE tokens
- token_to_midi: Convert BPE tokens back to MIDI

Usage:
    from bachgen.midi_bpe_token_style import music_xml_to_midi, midi_to_token
    
    # Convert pipeline
    midi_path = music_xml_to_midi("song.musicxml")
    tokens, token_path = midi_to_token(midi_path)
"""

from .music_xml_to_midi import music_xml_to_midi
from .midi_to_music_xml import midi_to_music_xml
from .midi_to_token import midi_to_token, load_tokens_from_file
from .token_to_midi import token_to_midi, tokens_from_raw_list

__all__ = [
    'music_xml_to_midi',
    'midi_to_music_xml', 
    'midi_to_token',
    'token_to_midi',
    'load_tokens_from_file',
    'tokens_from_raw_list'
]

__version__ = "1.0.0"