#!/usr/bin/env python3
"""
Convert MIDI to tokens using pretrained REMI tokenizer
"""

import sys
import json
from pathlib import Path
from miditok import REMI
from symusic import Score

def midi_to_token(midi_path, token_path=None, pretrained_model="Natooz/Maestro-REMI-bpe20k"):
    """
    Convert MIDI file to tokens using pretrained REMI tokenizer
    
    Args:
        midi_path (str or Path): Path to input MIDI file
        token_path (str or Path, optional): Path to output token file (JSON)
                                          If None, uses same name with .json extension
        pretrained_model (str): Pretrained model name from Hugging Face
    
    Returns:
        tuple: (tokens, Path to token file)
    """
    midi_path = Path(midi_path)
    
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    
    # Generate output path if not provided
    if token_path is None:
        token_path = midi_path.with_suffix('.json')
    else:
        token_path = Path(token_path)
    
    try:
        # Load pretrained REMI tokenizer
        print(f"Loading pretrained REMI tokenizer: {pretrained_model}")
        tokenizer = REMI.from_pretrained(pretrained_model)
        print(f"✓ Tokenizer loaded")
        print(f"  Vocabulary size: {len(tokenizer.vocab)}")
        print(f"  Special tokens: {tokenizer.special_tokens}")
        
        # Load MIDI file
        print(f"Loading MIDI: {midi_path}")
        score = Score(str(midi_path))
        
        # Display MIDI info
        print(f"✓ MIDI loaded:")
        print(f"  Duration: {score.end()} ticks")
        print(f"  Tracks: {len(score.tracks)}")
        
        # Tokenize
        print("Tokenizing...")
        tokens = tokenizer(score)
        
        # Display tokenization results
        if hasattr(tokens, '__len__') and len(tokens) > 0:
            if hasattr(tokens[0], 'tokens'):
                # Multiple tracks
                print(f"✓ Tokenized into {len(tokens)} track sequences:")
                total_tokens = 0
                token_data = []
                
                for i, track_tokens in enumerate(tokens):
                    track_token_count = len(track_tokens.tokens)
                    total_tokens += track_token_count
                    print(f"  Track {i}: {track_token_count} tokens")
                    print(f"    First 10 tokens: {track_tokens.tokens[:10]}")
                    
                    token_data.append({
                        'track_id': i,
                        'tokens': track_tokens.tokens,
                        'ids': track_tokens.ids if hasattr(track_tokens, 'ids') else None
                    })
                
                print(f"  Total tokens: {total_tokens}")
                
            else:
                # Single sequence
                token_count = len(tokens.tokens)
                print(f"✓ Tokenized into single sequence: {token_count} tokens")
                print(f"  First 20 tokens: {tokens.tokens[:20]}")
                
                token_data = {
                    'tokens': tokens.tokens,
                    'ids': tokens.ids if hasattr(tokens, 'ids') else None
                }
        
        # Save tokens to JSON
        print(f"Saving tokens: {token_path}")
        output_data = {
            'source_midi': str(midi_path),
            'tokenizer_model': pretrained_model,
            'token_data': token_data
        }
        
        with open(token_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✓ Token file created: {token_path}")
        
        return tokens, token_path
        
    except Exception as e:
        print(f"❌ Error converting MIDI to tokens: {e}")
        raise

def load_tokens_from_file(token_path):
    """
    Load tokens from JSON file
    
    Args:
        token_path (str or Path): Path to token JSON file
    
    Returns:
        dict: Token data
    """
    with open(token_path, 'r') as f:
        return json.load(f)

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python midi_to_token.py <input.mid> [output.json] [model_name]")
        print("Example: python midi_to_token.py song.mid song_tokens.json")
        print("Default model: Natooz/Maestro-REMI-bpe20k")
        sys.exit(1)
    
    midi_path = sys.argv[1]
    token_path = sys.argv[2] if len(sys.argv) > 2 else None
    model_name = sys.argv[3] if len(sys.argv) > 3 else "Natooz/Maestro-REMI-bpe20k"
    
    try:
        tokens, result_path = midi_to_token(midi_path, token_path, model_name)
        print(f"\n🎵 Tokenization completed successfully!")
        print(f"Input:  {midi_path}")
        print(f"Output: {result_path}")
        print(f"Model:  {model_name}")
        
    except Exception as e:
        print(f"\n❌ Tokenization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()