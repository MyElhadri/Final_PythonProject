import random

def draw_shape(draw_ctx, width, height, shape_dict):
    stype = shape_dict["type"]
    color = shape_dict["color"]
    x = shape_dict["x"]
    y = shape_dict["y"]
    size = shape_dict["size"]

    if stype == "circle":
        draw_ctx.ellipse([x-size, y-size, x+size, y+size], fill=color, outline="black")
    elif stype == "rectangle":
        w2 = random.randint(30,80)
        h2 = random.randint(30,80)
        draw_ctx.rectangle([x, y, x+w2, y+h2], fill=color, outline="black")
    elif stype == "triangle":
        points = [
            (x, y),
            (x+size, y+size),
            (x-size, y+size)
        ]
        draw_ctx.polygon(points, fill=color, outline="black")
    elif stype == "star":
        # On dessine un symbole "★"
        draw_ctx.text((x, y), "★", fill=color)
    elif stype == "hexagon":
        pts = []
        for i in range(6):
            xx = x + random.randint(-size,size)
            yy = y + random.randint(-size,size)
            pts.append((xx, yy))
        draw_ctx.polygon(pts, fill=color, outline="black")
    else:
        # Valeur par défaut
        draw_ctx.ellipse([x-size, y-size, x+size, y+size], fill=color, outline="black")
