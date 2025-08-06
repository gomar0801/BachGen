from bs4 import BeautifulSoup
from bs4.element import Tag
from fractions import Fraction
import pretty_midi
import copy

def extract_notes_with_positions(measure, divisions):
    notes_with_pos = []
    current_positions = {}  # position par voix
    last_positions = {}     # dernière position connue par voix
    print(f"\n[extract_notes_with_positions] Mesure {measure['number'] if measure.has_attr('number') else '?'}")

    for element in measure.children:
        if element.name == "note":
            voice = element.voice.text if element.voice else "1"
            duration = int(element.duration.text) if element.duration else 0

            # Si c'est un accord, réutiliser la dernière position de la même voix
            if element.chord:
                pos = last_positions.get(voice, current_positions.get(voice, 0))
                print(f"  → Accord détecté (voice {voice}) : position héritée = {pos}")
            else:
                pos = current_positions.get(voice, 0)

            # Pitch lisible pour debug
            if element.rest:
                pitch_str = "Rest"
            else:
                pitch_el = element.find("pitch")
                step = pitch_el.step.text if pitch_el else "?"
                alter = pitch_el.alter.text if pitch_el and pitch_el.alter else ""
                octave = pitch_el.octave.text if pitch_el else "?"
                alter_symbol = {"-2":"bb","-1":"b","0":"","1":"#","2":"##"}.get(alter, "")
                pitch_str = f"{step}{alter_symbol}{octave}"

            print(f"    • Note: {pitch_str}, Voice: {voice}, Start: {pos}, Duration: {duration}, Chord: {bool(element.chord)}")

            # Ajouter la note
            notes_with_pos.append({
                "note": element,
                "voice": voice,
                "start": pos,
                "duration": duration,
                "is_rest": bool(element.rest) # Changed from note.find("rest") to element.rest
            })

            # Si ce n'est PAS un accord, avancer la position de la voix
            if not element.chord:
                current_positions[voice] = pos + duration
                last_positions[voice] = pos  # garde la position de la dernière note pour accords

        elif element.name == "backup":
            dur = int(element.duration.text)
            print(f"  → Backup : -{dur}")
            for voice in current_positions.keys():
                current_positions[voice] -= dur

        elif element.name == "forward":
            dur = int(element.duration.text)
            print(f"  → Forward : +{dur}")
            for voice in current_positions.keys():
                current_positions[voice] += dur

    print(f"[Résultat] {len(notes_with_pos)} notes extraites avec positions.\n")
    return notes_with_pos

def rewrite_measure_as_single_voice(measure, soup):
    print(f"\n[rewrite_measure_as_single_voice] Réécriture de la mesure {measure.get('number')}")

    # Étape 1 : Extraire les notes avec positions
    notes_with_positions = extract_notes_with_positions(measure,1)
    print(f"\n  → {len(notes_with_positions)} notes extraites avec positions")

    # Étape 2 : Trier par position
    notes_with_positions.sort(key=lambda n: n["start"])
    print("  → Notes triées par position :")
    for n in notes_with_positions:
        label = "Rest" if n["is_rest"] else (
            n["note"].pitch.step.text +
            (("#" if n["note"].pitch.alter else "") if n["note"].pitch else "") +
            (n["note"].pitch.octave.text if n["note"].pitch else "")
        )
        print(f"    • Pos {n['start']:>5}, Voice {n['voice']}, Note: {label}")

    # Étape 3 : Grouper par position
    grouped_by_position = {}
    for n in notes_with_positions:
        grouped_by_position.setdefault(n["start"], []).append(n)

    # Étape 4 : Créer une nouvelle mesure
    new_measure = soup.new_tag("measure", number=measure.get("number"))

    for pos, group in grouped_by_position.items():
        print(f"\n  → Position {pos} : {len(group)} élément(s)")

        # Séparer notes et silences
        notes_only = [g for g in group if not g["is_rest"]]
        rests_only = [g for g in group if g["is_rest"]]

        if notes_only:
            # Supprimer les silences superposés à des notes
            if rests_only:
                print(f"    ⚠ Silences superposés détectés, ils sont ignorés.")
            
            # Ajouter les notes en accords
            for idx, item in enumerate(notes_only):
                note_clone = copy.copy(item["note"])
                note_clone.voice.string = "1"  # On force en voice 1

                if idx > 0:
                    # Ajouter <chord/> uniquement si non présent
                    if not note_clone.find("chord"):
                        chord_tag = soup.new_tag("chord")
                        note_clone.insert(0, chord_tag)

                new_measure.append(note_clone)

        else:
            # Aucun son, uniquement un silence => on le garde tel quel
            for item in rests_only:
                rest_clone = copy.copy(item["note"])
                rest_clone.voice.string = "1"
                new_measure.append(rest_clone)

    print(f"[rewrite_measure_as_single_voice] Mesure réécrite avec {len(new_measure.find_all('note'))} notes")
    return new_measure

def attributes_to_tokens(attributes, staff=None): # tokenize 'attributes' section in MusicXML
    print(f"[attributes_to_tokens] Attributs lus pour staff={staff}")
    tokens = []
    divisions = None

    for child in attributes.contents:
        type_ = child.name
        if type_ == 'divisions':
            divisions = int(child.text)
        elif type_ in ('clef', 'key', 'time'):
            if staff is not None:
                if 'number' in child.attrs and int(child['number']) != staff:
                    continue
            tokens.append(attribute_to_token(child))

    print(f"  → Tokens attributs : {tokens}, divisions={divisions}")
    return tokens, divisions

def attribute_to_token(child): # clef, key signature, and time signature
    type_ = child.name
    if type_ == 'clef':
        if child.sign.text == 'G':
            return 'clef_treble'
        elif child.sign.text == 'F':
            return 'clef_bass'
    elif type_ == 'key':
        key = int(child.fifths.text)
        if key < 0:
            return f'key_flat_{abs(key)}'
        elif key > 0:
            return f'key_sharp_{key}'
        else:
            return f'key_natural_{key}'
    elif type_ == 'time':
        beats = child.find('beats')
        beat_type = child.find('beat-type')
        if beats and beat_type:
            beats_val = int(beats.text)
            beat_type_val = int(beat_type.text)
            return f"time_{beats_val}/{beat_type_val}"  # ✅ Pas de simplification
        else:
            print("[attribute_to_token] ⚠ Impossible de lire le time correctement")
            return None

def aggregate_notes(voice_notes): # notes to chord
    for note in voice_notes[1:]:
        if note.chord is not None:
            last_note = note.find_previous('note')
            last_note.insert(0, note.pitch)
            note.decompose()

def note_to_tokens(note, divisions=8, note_name=True): # notes and rests
    print("[note_to_tokens] Traitement d'une note ou d'un groupe")
    ######################
    # Ignorer les notes invisibles (print-object="no")
    if 'print-object' in note.attrs and note['print-object'] == 'no':
        print("  → Note transparente détectée, ignorée")
        return []
    ######################
    
    beam_translations = {'begin': 'start', 'end': 'stop', 'forward hook': 'partial-right', 'backward hook': 'partial-left'}

    if note.duration is None: # gracenote
        return []

    duration_in_fraction = str(Fraction(int(note.duration.text), divisions))

    if note.rest:
        print("  → Rest detected")
        print(f"  → Tokens générés : ['rest', 'len_{duration_in_fraction}']")
        return ['rest', f'len_{duration_in_fraction}'] # for rests

    tokens = []

    # pitches
    for pitch in note.find_all('pitch'):
        if note_name:
            if pitch.alter:
                alter_to_symbol= {'-2': 'bb', '-1': 'b', '0':'', '1': '#', '2': '##'}
                tokens.append(f"note_{pitch.step.text}{alter_to_symbol[pitch.alter.text]}{pitch.octave.text}")
            else:
                tokens.append(f"note_{pitch.step.text}{pitch.octave.text}")
        else:
            note_number = pretty_midi.note_name_to_number(pitch.step.text + pitch.octave.text) # 'C4' -> 60
            if pitch.alter:
                note_number += int(pitch.alter.text)
            tokens.append(f'note_{note_number}')

    # len
    tokens.append(f'len_{duration_in_fraction}')

    if note.stem:
        tokens.append(f'stem_{note.stem.text}')

    if note.beam:
        beams = note.find_all('beam')
        tokens.append('beam_' + '_'.join([beam_translations[b.text] if b.text in beam_translations else b.text for b in beams]))

    if note.tied:
        tokens.append('tie_' + note.tied.attrs['type'])
    
    # Variables à afficher dans le print
    pitches = [t for t in tokens if t.startswith('note_')]
    duration = int(note.duration.text)
    stem = note.stem.text if note.stem else "none"
    beams = [b.text for b in note.find_all('beam')] if note.beam else []
    ties = [note.tied.attrs['type']] if note.tied else []
    print(f"  → Pitches : {pitches}, duration: {duration / divisions}, stem: {stem}, beams: {beams}, ties: {ties}")
    print(f"  → Tokens générés : {tokens}")
    
    return tokens

def element_segmentation(measure, soup, staff=None): # divide elements into three sections
    print("[element_segmentation] Segmentation des éléments par voix")
    voice_starts, voice_ends = {}, {}
    position = 0
    for element in measure.contents:
        if element.name == 'note':
            if element.duration is None: # gracenote
                continue

            voice = element.voice.text
            duration = int(element.duration.text)
            if element.chord: # rewind for concurrent notes
                position -= last_duration

            if element.staff and int(element.staff.text) == staff:
                voice_starts[voice] = min(voice_starts[voice], position) if voice in voice_starts else position
                start_tag = soup.new_tag('start')
                start_tag.string = str(position)
                element.append(start_tag)

            position += duration

            if element.staff and int(element.staff.text) == staff:
                voice_ends[voice] = max(voice_ends[voice], position) if voice in voice_ends else position
                end_tag = soup.new_tag('end')
                end_tag.string = str(position)
                element.append(end_tag)

            last_duration = duration
        elif element.name == 'backup':
            position -= int(element.duration.text)
        elif element.name == 'forward':
            position += int(element.duration.text)
        else: # other types
            start_tag = soup.new_tag('start')
            end_tag = soup.new_tag('end')

            start_tag.string = str(position)
            end_tag.string = str(position)

            element.append(start_tag)
            element.append(end_tag)

    # voice section
    voice_start = sorted(voice_starts.values())[1] if voice_starts else 0
    voice_end = sorted(voice_ends.values(), reverse=True)[1] if voice_ends else 0

    pre_voice_elements, post_voice_elements, voice_elements = [], [], []
    for element in measure.contents:
        if element.name in ('backup', 'forward'):
            continue
        if element.name == 'note' and element.duration is None: # gracenote
            continue
        if staff is not None:
            if element.staff and int(element.staff.text) != staff:
                continue

        if voice_starts or voice_ends:
            if int(element.end.text) <= voice_start:
                pre_voice_elements.append(element)
            elif voice_end <= int(element.start.text):
                post_voice_elements.append(element)
            else:
                voice_elements.append(element)
        else:
            pre_voice_elements.append(element)
          
    print(f"  ↪ Pré-voix : {len(pre_voice_elements)}, Voix : {len(voice_elements)}, Post-voix : {len(post_voice_elements)}")
    return pre_voice_elements, voice_elements, post_voice_elements

def measures_to_tokens(measures, soup, staff=None, note_name=True):
    divisions = 0
    tokens = []

    for measure in measures:
        print(f"\n[Mesure {measure['number']}]")

        tokens.append('bar')

        # Sélection des notes selon le staff
        if staff is not None:
            notes = [n for n in measure.find_all('note') if n.staff and int(n.staff.text) == staff]
        else:
            notes = measure.find_all('note')

        voices = list(set([n.voice.text for n in notes if n.voice]))

        # Si aucune voix détectée, attribuer la voix 1
        if not voices:
            for n in notes:
                if not n.voice:
                    new_voice_tag = soup.new_tag("voice")
                    new_voice_tag.string = "1"
                    n.append(new_voice_tag)
            voices = ["1"]

        print(f"  → Voix détectées : {voices}")

        # === NOUVEAU : fusion automatique des mesures multi-voix ===
        if len(voices) > 1:
            print("  → Mesure multi-voix détectée : fusion avec rewrite_measure_as_single_voice")
            measure = rewrite_measure_as_single_voice(measure, soup)
            # Après fusion, recalculer les notes et voix
            notes = measure.find_all('note')
            voices = ["1"]

        # Agrégation des accords (dans chaque voix)
        for voice in voices:
            voice_notes = [n for n in notes if n.voice and n.voice.text == voice]
            print(f"    • Agrégation notes voix {voice} : {len(voice_notes)} éléments")
            aggregate_notes(voice_notes)

        # Tokenisation classique après fusion
        for element in measure.contents:
            if staff is not None:
                if element.name in ('attributes', 'note') and element.staff and int(element.staff.text) != staff:
                    continue
            if element.name == 'attributes':
                attr_tokens, div = attributes_to_tokens(element, staff)
                tokens += attr_tokens
                divisions = div if div else divisions
            elif element.name == 'note':
                tokens += note_to_tokens(element, divisions, note_name)

    return tokens



def load_MusicXML(mxml_path): # load MusicXML contents using BeautifulSoup
    soup = BeautifulSoup(open(mxml_path, encoding='utf-8'), 'lxml-xml', from_encoding='utf-8') # MusicXML
    print(f"[load_MusicXML] Chargement de {mxml_path}")
    for tag in soup(string='\n'): # eliminate line breaks
        tag.extract()

    parts = soup.find_all('part')

    return [part.find_all('measure') for part in parts], soup
    print(f"→ {len(measures)} mesures chargées")

def MusicXML_to_tokens(soup_or_mxml_path, note_name=True): # use this method
    print("\n=== Début de MusicXML_to_tokens ===")
    if type(soup_or_mxml_path) is str:
        parts, soup = load_MusicXML(soup_or_mxml_path)
    else:
        soup = soup_or_mxml_path
        for tag in soup(string='\n'): # eliminate line breaks
            tag.extract()

        parts = [part.find_all('measure') for part in soup.find_all('part')]

    if len(parts) == 1:
        tokens = ['R'] + measures_to_tokens(parts[0], soup, staff=1, note_name=note_name)
        tokens += ['L'] + measures_to_tokens(parts[0], soup, staff=2, note_name=note_name)
    elif len(parts) == 2:
        tokens = ['R'] + measures_to_tokens(parts[0], soup, note_name=note_name)
        tokens += ['L'] + measures_to_tokens(parts[1], soup, note_name=note_name)
    
    print("=== Fin de MusicXML_to_tokens ===")
    return tokens