from PIL import Image, ImageOps, ImageFilter, ImageChops
import os
import random
import string

def generate_random_filename(extension="png"):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "." + extension


from PIL import Image, ImageOps, ImageFilter, ImageChops
import os
import uuid


def apply_filter(image_path, filter_name, output_folder):
    img = Image.open(image_path).convert("RGB")

    if filter_name == 'grayscale':
        img = ImageOps.grayscale(img)
    elif filter_name == 'sepia':
        sepia_img = ImageOps.colorize(ImageOps.grayscale(img), "#704214", "#C0A080")
        img = sepia_img
    elif filter_name == 'invert':
        img = ImageOps.invert(img)
    elif filter_name == 'blur':
        img = img.filter(ImageFilter.BLUR)
    elif filter_name == 'glitch':
        r, g, b = img.split()
        r = ImageChops.offset(r, 10, 0)
        img = Image.merge('RGB', (r, g, b))

    # On génère un nom unique
    processed_filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(output_folder, processed_filename)
    img.save(output_path)

    return processed_filename
