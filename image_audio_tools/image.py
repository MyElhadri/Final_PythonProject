from PIL import Image, ImageOps, ImageFilter, ImageChops, ImageEnhance
import os
import uuid


def apply_filter(image_path, filter_name, output_folder):
    img = Image.open(image_path).convert("RGB")

    # 🌟 **Filtres classiques**
    if filter_name == 'grayscale':
        img = ImageOps.grayscale(img)
    elif filter_name == 'sepia':
        img = ImageOps.colorize(ImageOps.grayscale(img), "#704214", "#C0A080")
    elif filter_name == 'invert':
        img = ImageOps.invert(img)
    elif filter_name == 'blur':
        img = img.filter(ImageFilter.BLUR)
    elif filter_name == 'glitch':
        r, g, b = img.split()
        r = ImageChops.offset(r, 10, 0)
        img = Image.merge('RGB', (r, g, b))

    # 🎨 **Effets créatifs et artistiques**
    elif filter_name == 'oil_painting':
        img = img.filter(ImageFilter.ModeFilter(size=10))  # Simule une peinture à l'huile
    elif filter_name == 'sketch':
        img = img.convert('L').filter(ImageFilter.CONTOUR)  # Simule un dessin au crayon
    elif filter_name == 'neon_glow':
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        img = ImageOps.colorize(img.convert('L'), "#0000FF", "#FF00FF")  # Effet néon
    elif filter_name == 'dreamy_blur':
        img = img.filter(ImageFilter.GaussianBlur(radius=8))  # Effet flou doux
    elif filter_name == 'pastel':
        img = img.filter(ImageFilter.SMOOTH).filter(ImageFilter.SMOOTH_MORE)
        img = ImageEnhance.Color(img).enhance(1.5)  # Couleurs plus pastel
    elif filter_name == 'mosaic':
        img = img.resize((img.width // 20, img.height // 20), Image.NEAREST)
        img = img.resize((img.width * 20, img.height * 20), Image.NEAREST)  # Pixelisation améliorée
    elif filter_name == 'halftone':
        img = img.convert('L').filter(ImageFilter.FIND_EDGES)  # Simule un effet d’impression
    elif filter_name == 'cartoon':
        img = img.filter(ImageFilter.EDGE_ENHANCE)
        img = ImageOps.posterize(img, 3)  # Effet cartoon en réduisant les couleurs
    elif filter_name == 'pop_art':
        img = ImageEnhance.Color(img).enhance(3.0)
        img = ImageOps.posterize(img, 4)  # Effet pop-art coloré
    elif filter_name == 'vintage':
        img = ImageOps.colorize(ImageOps.grayscale(img), "#8B4513", "#FFD700")  # Ton chaud vintage

    # 📸 **Enregistrement de l’image traitée**
    processed_filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(output_folder, processed_filename)
    img.save(output_path)

    return processed_filename
