#!/usr/bin/env python3
"""
Convert MusicXML to MIDI using symusic
"""

import sys
from pathlib import Path
from symusic import Score

def music_xml_to_midi(xml_path, midi_path=None):
    """
    Convert MusicXML file to MIDI file using symusic
    
    Args:
        xml_path (str or Path): Path to input MusicXML file
        midi_path (str or Path, optional): Path to output MIDI file
                                         If None, uses same name with .mid extension
    
    Returns:
        Path: Path to the created MIDI file
    """
    xml_path = Path(xml_path)
    
    if not xml_path.exists():
        raise FileNotFoundError(f"MusicXML file not found: {xml_path}")
    
    # Generate output path if not provided
    if midi_path is None:
        midi_path = xml_path.with_suffix('.mid')
    else:
        midi_path = Path(midi_path)
    
    try:
        # Load MusicXML file
        from music21 import converter
        
        print(f"Loading MusicXML: {xml_path}")
        score = converter.parse(str(xml_path))
        
        # Display basic info using music21
        print(f"✓ Loaded successfully:")
        print(f"  Duration: {score.duration.quarterLength} quarter notes")
        print(f"  Parts: {len(score.parts)}")
        
        for i, part in enumerate(score.parts):
            notes = part.flatten().notes
            instrument = part.getInstrument()
            print(f"  Part {i}: {len(notes)} notes, instrument: {instrument}")
        
        # Save as MIDI using music21
        print(f"Saving MIDI: {midi_path}")
        score.write('midi', fp=str(midi_path))
        print(f"✓ MIDI file created: {midi_path}")
        
        return midi_path
        
    except Exception as e:
        print(f"❌ Error converting MusicXML to MIDI: {e}")
        raise

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python music_xml_to_midi.py <input.musicxml> [output.mid]")
        print("Example: python music_xml_to_midi.py song.musicxml song.mid")
        sys.exit(1)
    
    xml_path = sys.argv[1]
    midi_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result_path = music_xml_to_midi(xml_path, midi_path)
        print(f"\n🎵 Conversion completed successfully!")
        print(f"Input:  {xml_path}")
        print(f"Output: {result_path}")
        
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()