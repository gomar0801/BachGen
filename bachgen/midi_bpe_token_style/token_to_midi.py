#!/usr/bin/env python3
"""
Convert tokens back to MIDI using pretrained REMI tokenizer
"""

import sys
import json
from pathlib import Path
from miditok import REMI, TokSequence

def token_to_midi(token_path, midi_path=None, pretrained_model="Natooz/Maestro-REMI-bpe20k"):
    """
    Convert tokens back to MIDI file using pretrained REMI tokenizer
    
    Args:
        token_path (str or Path): Path to input token file (JSON)
        midi_path (str or Path, optional): Path to output MIDI file
                                         If None, uses same name with .mid extension
        pretrained_model (str): Pretrained model name from Hugging Face
    
    Returns:
        Path: Path to the created MIDI file
    """
    token_path = Path(token_path)
    
    if not token_path.exists():
        raise FileNotFoundError(f"Token file not found: {token_path}")
    
    # Generate output path if not provided
    if midi_path is None:
        midi_path = token_path.with_suffix('.mid')
    else:
        midi_path = Path(midi_path)
    
    try:
        # Load token data
        print(f"Loading tokens: {token_path}")
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        
        print(f"✓ Token data loaded")
        print(f"  Source: {token_data.get('source_midi', 'unknown')}")
        print(f"  Model: {token_data.get('tokenizer_model', 'unknown')}")
        
        # Load pretrained REMI tokenizer
        print(f"Loading pretrained REMI tokenizer: {pretrained_model}")
        tokenizer = REMI.from_pretrained(pretrained_model)
        print(f"✓ Tokenizer loaded")
        
        # Reconstruct token sequences
        tokens_info = token_data['token_data']
        
        if isinstance(tokens_info, list):
            # Multiple tracks
            print(f"Reconstructing {len(tokens_info)} track sequences...")
            token_sequences = []
            
            for i, track_data in enumerate(tokens_info):
                track_tokens = track_data['tokens']
                print(f"  Track {i}: {len(track_tokens)} tokens")
                
                # Create TokSequence object
                tok_seq = TokSequence(tokens=track_tokens)
                if track_data.get('ids'):
                    tok_seq.ids = track_data['ids']
                
                token_sequences.append(tok_seq)
            
            tokens = token_sequences
            
        else:
            # Single sequence
            track_tokens = tokens_info['tokens']
            print(f"Reconstructing single sequence: {len(track_tokens)} tokens")
            
            # Create TokSequence object
            tokens = TokSequence(tokens=track_tokens)
            if tokens_info.get('ids'):
                tokens.ids = tokens_info['ids']
        
        # Convert tokens back to MIDI
        print("Converting tokens to MIDI...")
        reconstructed_score = tokenizer(tokens)
        
        # Display reconstruction info
        print(f"✓ MIDI reconstructed:")
        print(f"  Duration: {reconstructed_score.end()} ticks")
        print(f"  Tracks: {len(reconstructed_score.tracks)}")
        
        for i, track in enumerate(reconstructed_score.tracks):
            print(f"  Track {i}: {len(track.notes)} notes, program {track.program}")
        
        # Save MIDI file
        print(f"Saving MIDI: {midi_path}")
        reconstructed_score.dump_midi(str(midi_path))
        print(f"✓ MIDI file created: {midi_path}")
        
        return midi_path
        
    except Exception as e:
        print(f"❌ Error converting tokens to MIDI: {e}")
        raise

def tokens_from_raw_list(token_list, midi_path, pretrained_model="Natooz/Maestro-REMI-bpe20k"):
    """
    Convert raw token list directly to MIDI (useful for generation)
    
    Args:
        token_list (list): List of token strings
        midi_path (str or Path): Path to output MIDI file
        pretrained_model (str): Pretrained model name
    
    Returns:
        Path: Path to the created MIDI file
    """
    midi_path = Path(midi_path)
    
    try:
        # Load tokenizer
        print(f"Loading tokenizer: {pretrained_model}")
        tokenizer = REMI.from_pretrained(pretrained_model)
        
        # Create token sequence
        print(f"Processing {len(token_list)} tokens...")
        tokens = TokSequence(tokens=token_list)
        
        # Convert to MIDI
        print("Converting to MIDI...")
        score = tokenizer(tokens)
        
        # Save
        score.dump_midi(str(midi_path))
        print(f"✓ MIDI saved: {midi_path}")
        
        return midi_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python token_to_midi.py <input_tokens.json> [output.mid] [model_name]")
        print("Example: python token_to_midi.py song_tokens.json reconstructed.mid")
        print("Default model: Natooz/Maestro-REMI-bpe20k")
        sys.exit(1)
    
    token_path = sys.argv[1]
    midi_path = sys.argv[2] if len(sys.argv) > 2 else None
    model_name = sys.argv[3] if len(sys.argv) > 3 else "Natooz/Maestro-REMI-bpe20k"
    
    try:
        result_path = token_to_midi(token_path, midi_path, model_name)
        print(f"\n🎵 Token-to-MIDI conversion completed successfully!")
        print(f"Input:  {token_path}")
        print(f"Output: {result_path}")
        print(f"Model:  {model_name}")
        
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()