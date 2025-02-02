import os
import uuid
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, current_app

# Create the blueprint for style transfer
style_transfer_bp = Blueprint('style_transfer', __name__)

# Load the TensorFlow Hub module once to avoid reloading on each request.
hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')

def load_img_from_bytes(img_bytes, max_dim=512):
    """Load and preprocess an image from raw bytes."""
    img = tf.image.decode_image(img_bytes, channels=3, dtype=tf.float32)
    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]  # Add batch dimension.
    return img

def tensor_to_image(tensor):
    """Convert a tensor to a PIL Image."""
    tensor = tensor * 255
    tensor = tf.clip_by_value(tensor, 0, 255)
    tensor = tf.cast(tensor, tf.uint8).numpy()
    if tensor.shape[0] == 1:
        tensor = tensor[0]
    return Image.fromarray(tensor)

@style_transfer_bp.route('/style-transfer', methods=['GET', 'POST'])
def style_transfer():
    if request.method == 'POST':
        # Ensure both files are uploaded.
        if 'content_image' not in request.files or 'style_image' not in request.files:
            return redirect(request.url)
        content_file = request.files['content_image']
        style_file = request.files['style_image']
        if content_file.filename == '' or style_file.filename == '':
            return redirect(request.url)

        # Generate unique filenames for each image.
        content_filename = f"content_{uuid.uuid4().hex}.png"
        style_filename = f"style_{uuid.uuid4().hex}.png"
        output_filename = f"output_{uuid.uuid4().hex}.png"

        # Get the upload folder from the Flask config; ensure it exists.
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/images')
        os.makedirs(upload_folder, exist_ok=True)
        content_path = os.path.join(upload_folder, content_filename)
        style_path = os.path.join(upload_folder, style_filename)
        output_path = os.path.join(upload_folder, output_filename)

        # Save the uploaded images.
        content_file.save(content_path)
        style_file.save(style_path)

        # Read the saved files.
        with open(content_path, 'rb') as f:
            content_bytes = f.read()
        with open(style_path, 'rb') as f:
            style_bytes = f.read()

        # Preprocess the images.
        content_img = load_img_from_bytes(content_bytes)
        style_img = load_img_from_bytes(style_bytes)

        # Run style transfer using the TensorFlow Hub module.
        stylized_tensor = hub_module(tf.constant(content_img), tf.constant(style_img))[0]
        output_img = tensor_to_image(stylized_tensor)
        output_img.save(output_path)

        # Build URL for the output image so it can be displayed in the template.
        output_url = url_for('static', filename='images/' + output_filename)
        return render_template(
            'style_transfer.html',
            result_image=output_url,
            content_image=content_filename,
            style_image=style_filename
        )
    # For GET requests, simply render the form.
    return render_template('style_transfer.html', result_image=None)
