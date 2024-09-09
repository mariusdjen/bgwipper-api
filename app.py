from flask import Flask, request, jsonify, send_file
import os
from rembg import remove
from PIL import Image
import uuid

app = Flask(__name__)

# Chemin du dossier où les images seront sauvegardées
output_dir = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(output_dir, exist_ok=True)  # Créez le dossier s'il n'existe pas

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    # Vérifie si une image a été envoyée dans la requête
    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image trouvée'}), 400

    image_file = request.files['image']  # Récupère le fichier image
    input_image = Image.open(image_file)  # Ouvre l'image avec PIL
    
    # Génère un identifiant unique pour les noms de fichiers
    unique_id = str(uuid.uuid4()).replace('-', '')
    
    # Crée les noms de fichiers uniques pour l'image originale et l'image sans fond
    original_filename = f"{unique_id}_original.png"
    no_bg_filename = f"{unique_id}_no_bg.png"
    
    # Chemin complet pour sauvegarder l'image originale
    original_path = os.path.join(output_dir, original_filename)
    input_image.save(original_path)  # Sauvegarde l'image originale

    # Supprime l'arrière-plan de l'image
    output_image = remove(input_image)
    
    # Chemin complet pour sauvegarder l'image sans fond
    no_bg_path = os.path.join(output_dir, no_bg_filename)
    output_image.save(no_bg_path)  # Sauvegarde l'image sans fond

    # Retourne les chemins des images (originale et sans fond) via une réponse JSON
    return jsonify({
        'original_image': f'/download/{original_filename}',
        'no_bg_image': f'/download/{no_bg_filename}'
    })




@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Chemin complet vers le fichier demandé
    path = os.path.join(output_dir, filename)
    
    # Vérifie si le fichier existe, sinon retourne une erreur
    if os.path.exists(path):
        return send_file(path)  # Envoie le fichier au client
    else:
        return jsonify({'error': 'Fichier non trouvé'}), 404

if __name__ == '__main__':
    # Lancement de l'application Flask en mode debug
    app.run(debug=True)
