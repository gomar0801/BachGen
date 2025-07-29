#!/usr/bin/env python3
"""
Convert MIDI to MusicXML using music21, restoring metadata if available
"""

import sys
import json
from pathlib import Path
from music21 import converter, metadata, key, meter, clef, instrument, tempo

def load_metadata(midi_path):
    """
    Load metadata file if it exists
    
    Args:
        midi_path (Path): Path to MIDI file
        
    Returns:
        dict or None: Metadata if found, None otherwise
    """
    metadata_path = midi_path.with_suffix('.metadata.json')
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load metadata: {e}")
            return None
    return None

def apply_metadata_to_score(score, metadata_info):
    """
    Apply saved metadata to reconstructed score
    
    Args:
        score: music21 Score object
        metadata_info (dict): Saved metadata
    """
    print("Applying saved metadata...")
    
    # Apply global metadata
    if not hasattr(score, 'metadata') or not score.metadata:
        score.insert(0, metadata.Metadata())
    
    global_meta = metadata_info['global_elements']
    if global_meta['title']:
        score.metadata.title = global_meta['title']
    if global_meta['composer']:
        score.metadata.composer = global_meta['composer']
    
    # Apply time signatures
    if global_meta['time_signatures']:
        for ts_info in global_meta['time_signatures']:
            try:
                ts = meter.TimeSignature(f"{ts_info['numerator']}/{ts_info['denominator']}")
                # Apply to all parts at the correct offset
                for part in score.parts:
                    existing_ts = part.getElementsByClass(meter.TimeSignature)
                    if not existing_ts:
                        part.insert(ts_info['offset'], ts)
            except Exception as e:
                print(f"⚠️ Could not apply time signature: {e}")
    
    # Apply key signatures
    if global_meta['key_signatures']:
        for ks_info in global_meta['key_signatures']:
            try:
                ks = key.KeySignature(ks_info['sharps'])
                # Apply to all parts at the correct offset
                for part in score.parts:
                    existing_ks = part.getElementsByClass(key.KeySignature)
                    if not existing_ks:
                        part.insert(ks_info['offset'], ks)
            except Exception as e:
                print(f"⚠️ Could not apply key signature: {e}")
    
    # Apply part-specific information
    part_metadata = metadata_info['parts']
    for i, part in enumerate(score.parts):
        if i < len(part_metadata):
            part_info = part_metadata[i]
            
            # Set part name
            if part_info['name']:
                part.partName = part_info['name']
            
            # Apply clefs
            if part_info['clefs']:
                for clef_info in part_info['clefs']:
                    try:
                        # Parse clef type from string
                        clef_str = clef_info['string']
                        if 'TrebleClef' in clef_str:
                            clef_obj = clef.TrebleClef()
                        elif 'BassClef' in clef_str:
                            clef_obj = clef.BassClef()
                        elif 'AltoClef' in clef_str:
                            clef_obj = clef.AltoClef()
                        else:
                            clef_obj = clef.TrebleClef()  # Default
                        
                        existing_clefs = part.getElementsByClass(clef.Clef)
                        if not existing_clefs:
                            part.insert(clef_info['offset'], clef_obj)
                    except Exception as e:
                        print(f"⚠️ Could not apply clef: {e}")

def apply_defaults(score):
    """
    Apply default musical elements when no metadata is available
    """
    print("Applying default musical structure...")
    
    # Add basic metadata
    if not hasattr(score, 'metadata') or not score.metadata:
        score.insert(0, metadata.Metadata())
        score.metadata.title = 'Converted from MIDI'
        score.metadata.composer = 'Unknown'
    
    # Add basic musical structure that MIDI loses
    for i, part in enumerate(score.parts):
        # Add clef if missing
        if not part.getElementsByClass(clef.Clef):
            part.insert(0, clef.TrebleClef())
        
        # Add key signature if missing  
        if not part.getElementsByClass(key.KeySignature):
            part.insert(0, key.KeySignature(0))  # C major
            
        # Add time signature if missing
        if not part.getElementsByClass(meter.TimeSignature):
            part.insert(0, meter.TimeSignature('4/4'))
        
        # Set default part name
        if not part.partName:
            part.partName = f'Part {i+1}'

def midi_to_music_xml(midi_path, xml_path=None):
    """
    Convert MIDI file to MusicXML file using music21, restoring metadata if available
    
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
        
        # Try to load metadata
        metadata_info = load_metadata(midi_path)
        
        if metadata_info:
            print("✓ Found metadata file - restoring original structure")
            apply_metadata_to_score(score, metadata_info)
        else:
            print("⚠️ No metadata found - using defaults")
            apply_defaults(score)
        
        # Display basic info
        print(f"✓ Loaded successfully:")
        print(f"  Duration: {score.duration.quarterLength} quarter notes")
        print(f"  Parts: {len(score.parts)}")
        print(f"  Title: {getattr(score.metadata, 'title', 'Unknown')}")
        print(f"  Composer: {getattr(score.metadata, 'composer', 'Unknown')}")
        
        # Display parts info
        for i, part in enumerate(score.parts):
            notes = part.flatten().notes
            print(f"  Part {i}: {len(notes)} notes, '{part.partName}', {part.getInstrument()}")

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