#!/usr/bin/env python3
"""
Convert MusicXML to MIDI using music21, preserving metadata
"""

import sys
import json
from pathlib import Path
from music21 import converter

def extract_musical_metadata(score):
    """
    Extract all important musical information that MIDI loses
    """
    metadata = {
        'parts': [],
        'global_elements': {
            'time_signatures': [],
            'key_signatures': [], 
            'tempo_markings': [],
            'title': None,
            'composer': None
        }
    }
    
    # Extract global metadata
    if hasattr(score, 'metadata') and score.metadata:
        metadata['global_elements']['title'] = score.metadata.title
        metadata['global_elements']['composer'] = score.metadata.composer
    
    # Extract global musical elements
    flattened = score.flatten()
    
    # Time signatures
    for ts in flattened.getElementsByClass('TimeSignature'):
        metadata['global_elements']['time_signatures'].append({
            'offset': float(ts.offset),
            'numerator': ts.numerator,
            'denominator': ts.denominator,
            'string': str(ts)
        })
    
    # Key signatures
    for ks in flattened.getElementsByClass('KeySignature'):
        metadata['global_elements']['key_signatures'].append({
            'offset': float(ks.offset),
            'sharps': ks.sharps,
            'string': str(ks)
        })
    
    # Tempo markings
    for tempo in flattened.getElementsByClass('TempoIndication'):
        metadata['global_elements']['tempo_markings'].append({
            'offset': float(tempo.offset),
            'number': getattr(tempo, 'number', None),
            'string': str(tempo)
        })
    
    # Extract part-specific information
    for i, part in enumerate(score.parts):
        part_info = {
            'index': i,
            'name': part.partName or f'Part {i+1}',
            'instrument': str(part.getInstrument()) if part.getInstrument() else 'Piano',
            'clefs': [],
            'measures': len(part.getElementsByClass('Measure')),
            'note_count': len(part.flatten().notes)
        }
        
        # Extract clefs for this part
        for clef in part.flatten().getElementsByClass('Clef'):
            part_info['clefs'].append({
                'offset': float(clef.offset),
                'string': str(clef)
            })
        
        metadata['parts'].append(part_info)
    
    return metadata

def music_xml_to_midi(xml_path, midi_path=None):
    """
    Convert MusicXML file to MIDI file, preserving metadata
    
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
        print(f"Loading MusicXML: {xml_path}")
        score = converter.parse(str(xml_path))
        
        # Extract and save metadata BEFORE MIDI conversion
        print("Extracting musical metadata...")
        metadata = extract_musical_metadata(score)
        
        # Save metadata alongside MIDI
        metadata_path = midi_path.with_suffix('.metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved: {metadata_path}")
        
        # Display basic info using music21
        print(f"✓ Loaded successfully:")
        print(f"  Duration: {score.duration.quarterLength} quarter notes")
        print(f"  Parts: {len(score.parts)}")
        print(f"  Title: {metadata['global_elements']['title']}")
        print(f"  Composer: {metadata['global_elements']['composer']}")
        
        for i, part in enumerate(score.parts):
            notes = part.flatten().notes
            instrument = part.getInstrument()
            print(f"  Part {i}: {len(notes)} notes, '{metadata['parts'][i]['name']}', {instrument}")
        
        # Save as MIDI using music21
        print(f"Saving MIDI: {midi_path}")
        score.write('midi', fp=str(midi_path), 
           addDefaultInstruments=False,
           quantizePost=False)
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