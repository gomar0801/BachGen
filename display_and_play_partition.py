from music21 import converter

def display_and_play(xml_path, show_score=True, midi_path=None):
    """
    Affiche une partition et génère un fichier MIDI à partir d’un fichier MusicXML.

    Args:
        xml_path (str): chemin du fichier MusicXML (.musicxml)
        show_score (bool): True pour afficher la partition dans une fenêtre
        midi_path (str): chemin du fichier .midi à générer (facultatif)
    """
    score = converter.parse(xml_path)
    
    if show_score:
        score.show()  # Affiche la partition (peut ouvrir MuseScore ou une fenêtre PDF)

    if midi_path:
        score.write('midi', fp=midi_path)
