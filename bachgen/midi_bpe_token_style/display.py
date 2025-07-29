# Additional imports for MIDI display
from music21 import converter, stream
from symusic import Score
import pretty_midi
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

def display_midi_info(midi_path, show_notes=True):
    """
    Display MIDI file information and optionally show piano roll
    
    Args:
        midi_path (str): Path to MIDI file
        show_notes (bool): Whether to display piano roll visualization
    """
    print(f"\n🎹 MIDI FILE ANALYSIS: {midi_path}")
    print("-" * 40)
    
    try:
        # Load with symusic for detailed info
        score = Score(str(midi_path))
        print(f"Duration: {score.end()} ticks ({score.end() / score.tpq:.2f} beats)")
        print(f"Time division: {score.tpq} ticks per quarter note")
        print(f"Number of tracks: {len(score.tracks)}")
        
        # Track details
        total_notes = 0
        for i, track in enumerate(score.tracks):
            print(f"  Track {i}: {len(track.notes)} notes, '{track.name}', program {track.program}")
            total_notes += len(track.notes)
        
        print(f"Total notes: {total_notes}")
        
        if show_notes and total_notes > 0:
            # Create piano roll visualization
            try:
                pm = pretty_midi.PrettyMIDI(str(midi_path))
                
                # Get piano roll
                piano_roll = pm.get_piano_roll(fs=10)  # 10 Hz sampling
                
                # Plot piano roll
                plt.figure(figsize=(12, 6))
                plt.imshow(piano_roll, aspect='auto', origin='lower', cmap='Blues')
                plt.colorbar(label='Velocity')
                plt.xlabel('Time (0.1s)')
                plt.ylabel('MIDI Note')
                plt.title(f'Piano Roll: {Path(midi_path).name}')
                plt.tight_layout()
                plt.show()
                
            except Exception as e:
                print(f"  Note: Could not create piano roll visualization: {e}")
    
    except Exception as e:
        print(f"❌ Error analyzing MIDI: {e}")

def display_tokens(tokens_or_path, max_tokens=50):
    """
    Display tokenization results
    
    Args:
        tokens_or_path: Either token data or path to token JSON file
        max_tokens (int): Maximum number of tokens to display per track
    """
    print(f"\n🔤 TOKEN ANALYSIS")
    print("-" * 40)
    
    try:
        if isinstance(tokens_or_path, (str, Path)):
            # Load from file
            with open(tokens_or_path, 'r') as f:
                data = json.load(f)
            token_data = data['token_data']
            print(f"Source: {data.get('source_midi', 'unknown')}")
            print(f"Model: {data.get('tokenizer_model', 'unknown')}")
        else:
            # Direct token data
            token_data = tokens_or_path
        
        if isinstance(token_data, list):
            # Multiple tracks
            total_tokens = 0
            for i, track_data in enumerate(token_data):
                if isinstance(track_data, dict):
                    tokens = track_data['tokens']
                else:
                    tokens = track_data.tokens if hasattr(track_data, 'tokens') else track_data
                
                total_tokens += len(tokens)
                print(f"\nTrack {i}: {len(tokens)} tokens")
                print(f"  First {min(max_tokens, len(tokens))} tokens:")
                for j, token in enumerate(tokens[:max_tokens]):
                    print(f"    {j:2d}: {token}")
                if len(tokens) > max_tokens:
                    print(f"    ... and {len(tokens) - max_tokens} more tokens")
            
            print(f"\nTotal tokens across all tracks: {total_tokens}")
            
        else:
            # Single sequence
            if isinstance(token_data, dict):
                tokens = token_data['tokens']
            else:
                tokens = token_data.tokens if hasattr(token_data, 'tokens') else token_data
            
            print(f"Single sequence: {len(tokens)} tokens")
            print(f"First {min(max_tokens, len(tokens))} tokens:")
            for i, token in enumerate(tokens[:max_tokens]):
                print(f"  {i:2d}: {token}")
            if len(tokens) > max_tokens:
                print(f"  ... and {len(tokens) - max_tokens} more tokens")
        
        # Token type analysis
        if isinstance(token_data, list):
            all_tokens = []
            for track_data in token_data:
                if isinstance(track_data, dict):
                    all_tokens.extend(track_data['tokens'])
                else:
                    all_tokens.extend(track_data.tokens if hasattr(track_data, 'tokens') else track_data)
        else:
            if isinstance(token_data, dict):
                all_tokens = token_data['tokens']
            else:
                all_tokens = token_data.tokens if hasattr(token_data, 'tokens') else token_data
        
        # Analyze token types
        token_types = {}
        for token in all_tokens:
            token_type = token.split('_')[0] if '_' in token else token
            token_types[token_type] = token_types.get(token_type, 0) + 1
        
        print(f"\nToken type distribution:")
        for token_type, count in sorted(token_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_tokens)) * 100
            print(f"  {token_type:15s}: {count:4d} ({percentage:5.1f}%)")
    
    except Exception as e:
        print(f"❌ Error displaying tokens: {e}")