from tokens_to_score import tokens_to_score

def convert_tokens_to_musicxml(tokens, output_path):
    """
    Convertit une séquence de tokens en un fichier MusicXML (.musicxml).
    Args:
        tokens (List[str] or str): liste ou chaîne de tokens (doit contenir 'R' et 'L')
        output_path (str): chemin du fichier .musicxml de sortie
    """
    if isinstance(tokens, list):
        token_string = " ".join(tokens)
    else:
        token_string = tokens

    score = tokens_to_score(token_string,output_path)
    score.write('musicxml', fp=output_path)
