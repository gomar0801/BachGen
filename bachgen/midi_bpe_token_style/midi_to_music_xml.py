#!/usr/bin/env python3
"""
Convert MIDI to MusicXML using music21
"""

import sys
from pathlib import Path
from music21 import converter, metadata

def midi_to_music_xml(midi_path, xml_path=None):
    """
    Convert MIDI file to MusicXML file using music21
    
    Args:
        midi_path (str or Path): Path to input MIDI file
        xml_path (str or Path, optional): Path to output MusicXML file
                                        If None, uses same name with .musicxml extension
    
    Returns:
        Path: Path to the created MusicXML file
    """
    midi_path = Path(midi_path)
    
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    
    # Generate output path if not provided
    if xml_path is None:
        xml_path = midi_path.with_suffix('.musicxml')
    else:
        xml_path = Path(xml_path)
    
    try:
        # Load MIDI file
        print(f"Loading MIDI: {midi_path}")
        score = converter.parse(str(midi_path))
        
        # Display basic info
        print(f"✓ Loaded successfully:")
        print(f"  Duration: {score.duration.quarterLength} quarter notes")
        print(f"  Parts: {len(score.parts)}")
        print(f"  Time signatures: {[str(ts) for ts in score.getTimeSignatures()]}")
        print(f"  Key signatures: {[str(ks) for ks in score.getKeySignatures()]}")
        
        # Add metadata
        score.append(metadata.Metadata())
        score.metadata.title = f'Converted from {midi_path.name}'
        score.metadata.composer = 'MIDI Conversion'
        
        # Display parts info
        for i, part in enumerate(score.parts):
            notes = part.flatten().notes
            print(f"  Part {i}: {len(notes)} notes, instrument: {part.getInstrument()}")
        
        # Save as MusicXML
        print(f"Saving MusicXML: {xml_path}")
        score.write('musicxml', fp=str(xml_path))
        print(f"✓ MusicXML file created: {xml_path}")
        
        return xml_path
        
    except Exception as e:
        print(f"❌ Error converting MIDI to MusicXML: {e}")
        raise

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python midi_to_music_xml.py <input.mid> [output.musicxml]")
        print("Example: python midi_to_music_xml.py song.mid song.musicxml")
        sys.exit(1)
    
    midi_path = sys.argv[1]
    xml_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result_path = midi_to_music_xml(midi_path, xml_path)
        print(f"\n🎼 Conversion completed successfully!")
        print(f"Input:  {midi_path}")
        print(f"Output: {result_path}")
        
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()