import pytest
from bachgen.tokens_to_score import tokens_to_score

def test_minimal_tokens_to_score():
    """Test converting minimal tokens to music21 Score"""
    with open('token_sample/minimal.tokens', 'r') as f:
        token_string = f.read()
    
    score = tokens_to_score(token_string)
    
    # Basic assertions
    assert len(score.parts) == 2  # Right and left hand
    assert len(score.parts[0].measures(1, 1)) == 1  # First measure exists
    
    # Check right hand content
    right_hand = score.parts[0]
    measure = right_hand.measure(1)
    
    # Check attributes
    assert measure.clef.name == 'treble'
    assert measure.keySignature.sharps == 0
    assert measure.timeSignature.numerator == 4
    assert measure.timeSignature.denominator == 4
    
    # Check note
    notes = measure.notes
    assert len(notes) == 1
    assert notes[0].pitch.nameWithOctave == 'C4'
    assert notes[0].quarterLength == 4.0