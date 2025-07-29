# BachGen

# in a notebook:



```
!rm -rf BachGen && git clone https://github.com/gomar0801/BachGen.git
!chmod +x ./BachGen/scripts/setup.sh
!./BachGen/scripts/setup.sh


from bachgen.display_and_play_partition import display_and_play 

display_and_play('./BachGen/musicxml_sample/minimal.musicxml')
```

sample1=QmbbGKtZ9G6DkWxvSeU516c1ktWiFJmEbHGmR3JFtLAPyC
sample2=QmbbWCwo3rhaJ2wKL6H7aQPX9D6HfQxLZKPzzyKhYM68GA
sample3=Qmb3mYXSWTtd5JcSrGSamvS9xaht9hdmp3BQvuiKJfKQjY

# Test Structure

## Files
- `test_xml_to_tokens.py` - Tests MusicXML to token conversion
- `test_tokens_to_xml.py` - Tests token to music21 Score conversion  
- `test_roundtrip.py` - Tests complete round-trip conversion
- `conftest.py` - Shared fixtures and configuration

## Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test_xml_to_tokens.py

# Run with verbose output
pytest -v
```

## Sample Data
- MusicXML samples in `musicxml_sample/`
- Token samples in `token_sample/`

## Token Format
The minimal example produces:
```
R bar clef_treble key_natural_0 time_4/4 note_C4 len_4 L bar
```

Where:
- `R` = Right hand (treble staff)
- `L` = Left hand (bass staff)
- `bar` = Measure delimiter
- `clef_treble` = Treble clef
- `key_natural_0` = C major (0 sharps/flats)
- `time_4/4` = 4/4 time signature
- `note_C4` = C4 pitch
- `len_4` = Whole note (4 quarter notes)