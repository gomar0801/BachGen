from music21 import converter

def convert_mxl_to_musicxml(input_path, output_path):
    """
    Convertit un fichier .xml brut en un fichier MusicXML (.musicxml) en utilisant music21.
    Args:
        input_path (str): chemin du fichier .xml brut
        output_path (str): chemin de sortie du fichier .musicxml
    """
    score = converter.parse(input_path)
    score.write('musicxml', fp=output_path)