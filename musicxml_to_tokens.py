from score_to_tokens import MusicXML_to_tokens
 
def convert_musicxml_to_tokens(input_path, note_name=True):
    """
    Convertit un fichier MusicXML (.musicxml) en une liste de tokens pour l'apprentissage automatique.
    Args:
        input_path (str): chemin du fichier .musicxml
        note_name (bool): True pour encoder les noms de note (C4, D#4...), False pour des entiers MIDI
    Returns:
        List[str]: séquence de tokens
    """
    tokens = MusicXML_to_tokens(input_path, note_name=note_name)
    return tokens
