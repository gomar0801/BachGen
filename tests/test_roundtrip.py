import pytest
from bachgen.score_to_tokens import MusicXML_to_tokens
from bachgen.tokens_to_score import tokens_to_score
from music21 import converter

def test_xml_to_tokens_to_xml():
    """Test round-trip conversion: XML → tokens → XML"""
    # Load original score
    original_score = converter.parse('musicxml_sample/minimal.musicxml')
    
    # Convert to tokens
    tokens = MusicXML_to_tokens('musicxml_sample/minimal.musicxml')
    token_string = ' '.join(tokens)
    
    # Convert back to score
    reconstructed_score = tokens_to_score(token_string)
    
    # Compare key elements
    # Right hand comparison
    orig_rh = original_score.parts[0]
    recon_rh = reconstructed_score.parts[0]
    
    # Check measure count
    assert len(orig_rh.measures(1, None)) == len(recon_rh.measures(1, None))
    
    # Check first measure attributes
    orig_m1 = orig_rh.measure(1)
    recon_m1 = recon_rh.measure(1)
    
    assert orig_m1.clef.name == recon_m1.clef.name
    assert orig_m1.keySignature.sharps == recon_m1.keySignature.sharps
    assert orig_m1.timeSignature.ratioString == recon_m1.timeSignature.ratioString
    
    # Check notes
    orig_notes = list(orig_m1.notes)
    recon_notes = list(recon_m1.notes)
    
    assert len(orig_notes) == len(recon_notes)
    assert orig_notes[0].pitch.nameWithOctave == recon_notes[0].pitch.nameWithOctave
    assert orig_notes[0].quarterLength == recon_notes[0].quarterLength