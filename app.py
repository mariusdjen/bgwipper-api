from flask import Flask, request, jsonify, send_file, url_for
import os
from rembg import remove
from PIL import Image
import uuid

app = Flask(__name__)

# Path to the folder where images will be saved
output_dir = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(output_dir, exist_ok=True)  # Create the folder if it doesn't exist

# Allowed image extensions and their corresponding MIME types
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png'}

# Maximum allowed file size (in bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename, mimetype):
    # Check the file extension and MIME type
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and \
           mimetype in ALLOWED_MIME_TYPES

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    # Check if an image was sent in the request
    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image trouvée'}), 400  

    image_file = request.files['image']  # Get the image file

    # Check the file extension and MIME type
    if not allowed_file(image_file.filename, image_file.mimetype):
        return jsonify({'error': 'Format de fichier non supporté'}), 400  
    
    # Check the file size
    image_file.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
    file_size = image_file.tell()  # Get the file size
    image_file.seek(0)  # Reset the file cursor

    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': f'Le fichier dépasse la taille maximale de {MAX_FILE_SIZE / (1024 * 1024)} Mo'}), 400  

    # Open the image with PIL
    try:
        input_image = Image.open(image_file)
    except Exception as e:
        return jsonify({'error': f'Erreur de traitement de l\'image: {str(e)}'}), 400  
    
    # Generate a unique ID for filenames
    unique_id = str(uuid.uuid4()).replace('-', '')
    
    # Create unique filenames for the original and background-removed images
    original_filename = f"{unique_id}_original.png"
    no_bg_filename = f"{unique_id}_no_bg.png"
    
    # Full path to save the original image
    original_path = os.path.join(output_dir, original_filename)
    input_image.save(original_path, format="PNG")  # Save the original image

    # Remove the background from the image
    output_image = remove(input_image)
    
    # Full path to save the background-removed image
    no_bg_path = os.path.join(output_dir, no_bg_filename)
    output_image.save(no_bg_path, format="PNG", optimize=True)  # Save the background-removed image with compression

    # Generate full URLs for downloading the images
    original_image_url = request.host_url + 'download/' + original_filename
    no_bg_image_url = request.host_url + 'download/' + no_bg_filename

    # Return the paths of the images (original and background-removed) via a JSON response
    return jsonify({
        'original_image_url': original_image_url,
        'no_bg_image_url': no_bg_image_url
    })

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Full path to the requested file
    path = os.path.join(output_dir, filename)

    # Check if the file exists, otherwise return an error
    if os.path.exists(path):
        return send_file(path)  # Send the file to the client
    else:
        return jsonify({'error': 'Fichier non trouvé'}), 404  
    
if __name__ == '__main__':
    # Start the Flask application
    app.run(debug=False)  # Deploy with debug=False in production


