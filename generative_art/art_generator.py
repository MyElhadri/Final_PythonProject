from PIL import Image, ImageDraw
import random
import os
from .shapes import draw_shape


def generate_random_art(num_shapes, shape_type, color_scheme, custom_color=None):
    """
    Génère un fichier d'art génératif avec des formes aléatoires.

    :param num_shapes: Nombre de formes à générer
    :param shape_type: Type de forme ('circle', 'rectangle', etc.)
    :param color_scheme: Palette de couleurs ('chaud', 'froid', 'random', 'custom')
    :param custom_color: Couleur personnalisée HEX si color_scheme="custom"
    :return: Nom du fichier généré et liste des formes
    """
    shapes = []
    for _ in range(num_shapes):
        shape = _random_shape_dict(shape_type, color_scheme, custom_color)
        shapes.append(shape)

    filename = f"art_{random.randint(1000, 9999)}.png"
    create_image_from_shapes(shapes, filename)
    return filename, shapes


def create_image_from_shapes(shape_list, filename):
    """
    Crée une image avec les formes spécifiées et l'enregistre.

    :param shape_list: Liste des formes à dessiner
    :param filename: Nom du fichier de sortie
    """
    width, height = 400, 400
    img = Image.new("RGB", (width, height), "white")
    draw_ctx = ImageDraw.Draw(img)

    for shape in shape_list:
        draw_shape(draw_ctx, width, height, shape)

    path = os.path.join("static/art", filename)
    img.save(path)


def _random_shape_dict(shape_type, color_scheme, custom_color=None):
    """
    Génère un dictionnaire représentant une forme aléatoire.

    :param shape_type: Type de forme spécifique ou 'mixed' pour aléatoire
    :param color_scheme: Palette de couleurs ('chaud', 'froid', 'random', 'custom')
    :param custom_color: Couleur personnalisée HEX si color_scheme="custom"
    :return: Dictionnaire contenant les caractéristiques de la forme
    """
    # Définition de la couleur
    if color_scheme == "custom" and custom_color:
        color = hex_to_rgb(custom_color)
    else:
        color = _get_color(color_scheme)

    # Sélection aléatoire du type de forme si "mixed"
    if shape_type.lower() == "mixed":
        shape_type = random.choice(["circle", "rectangle", "triangle", "star", "hexagon"])

    # Coordonnées et taille aléatoires
    x = random.randint(50, 350)
    y = random.randint(50, 350)
    size = random.randint(20, 50)

    return {"type": shape_type.lower(), "color": color, "x": x, "y": y, "size": size}


def _get_color(scheme):
    """
    Renvoie une couleur en fonction du schéma de couleurs sélectionné.

    :param scheme: 'chaud', 'froid', ou 'random'
    :return: Tuple RGB (r, g, b)
    """
    color_schemes = {
        "chaud": [(255, 100, 0), (255, 165, 0), (255, 69, 0), (255, 0, 0)],
        "froid": [(0, 100, 255), (100, 149, 237), (135, 206, 250), (0, 255, 255)]
    }

    return random.choice(
        color_schemes.get(scheme.lower(), [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]))


def hex_to_rgb(hexcolor):
    """
    Convertit une couleur HEX en format RGB.

    :param hexcolor: Code HEX sous la forme "#RRGGBB"
    :return: Tuple RGB (r, g, b)
    """
    hexcolor = hexcolor.lstrip("#")  # Supprime le "#"
    return tuple(int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))

