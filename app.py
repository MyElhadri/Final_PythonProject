import os
# Suppress some of TensorFlow's info and warning messages.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # 0 = all messages; 2 = warnings and info suppressed

from flask import (
    Flask, render_template, request, send_from_directory,
    redirect, url_for, send_file, jsonify
)
import os
import random
import io
import secrets
import shutil

# -- Internal and Third-Party Libraries --
# Generators for art
from generative_art.art_generator import create_image_from_shapes, generate_random_art
# Data visualization
from data_visualizations.data_viz_logic import load_weather_data, create_swirl_chart
# Audio tools
from image_audio_tools.audio_tools import generate_random_melody, change_audio_speed, merge_audio_files
from pydub import AudioSegment
from pydub.generators import Sine
# Image filters
from image_audio_tools.image import apply_filter
# Machine Learning: Markov text generation
from ml_features.text_generation import generate_markov_text
# Import the style transfer blueprint (this will import TensorFlow, which may take a while)
from ml_features.style_transfer import style_transfer_bp

# --------------------------------------------------------------
# Flask Application Configuration
# --------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "secret-key"

# Ensure directories exist for uploads and art
IMAGES_FOLDER = os.path.join("static", "images")
ART_FOLDER = os.path.join("static", "art")
GALLERY_FOLDER = os.path.join("static", "gallery")
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(ART_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = IMAGES_FOLDER  # used for style transfer

# Register the style transfer blueprint so its routes become available.
app.register_blueprint(style_transfer_bp)

# For storing art data (for generative art)
ART_DATA = {}

# Random statements for data visualization
STATEMENTS = [
    "📊 Today's data tells a unique story!",
    "🌦️ A deep dive into weather patterns!",
    "🎨 Visualizing the beauty of data!",
    "📈 Weather trends are always changing!",
    "🔎 Discover insights hidden in the numbers!",
    "🌍 Data speaks louder than words!",
    "📡 Tracking the sky one dataset at a time!",
    "💡 Each dataset reveals something new!",
]

# --------------------------------------------------------------
# 1. HOME ROUTE
# --------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

# --------------------------------------------------------------
# 2. GENERATIVE ART ROUTES
# --------------------------------------------------------------
@app.route("/art", methods=["GET", "POST"])
def art():
    filenames = []
    if request.method == "POST":
        num_shapes = int(request.form.get("num_shapes", 20))
        shape_type = request.form.get("shape_type", "mixed")
        color_scheme = request.form.get("color_scheme", "random")
        custom_color = request.form.get("custom_color") if color_scheme == "custom" else None

        # Generate 4 artworks
        for _ in range(4):
            filename, shape_list = generate_random_art(num_shapes, shape_type, color_scheme, custom_color)
            ART_DATA[filename] = shape_list
            filenames.append(filename)

    return render_template("art.html", filenames=filenames)

@app.route("/edit_art/<filename>", methods=["GET", "POST"])
def edit_art(filename):
    if filename not in ART_DATA:
        return redirect(url_for("art"))

    shape_list = ART_DATA[filename]

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_shape":
            new_type = request.form["shape_type"]
            hexcolor = request.form["shape_color"]
            color = hex_to_rgb(hexcolor)
            x, y = random.randint(50, 350), random.randint(50, 350)
            size = random.randint(20, 50)
            shape_list.append({
                "type": new_type,
                "color": color,
                "x": x, "y": y, "size": size
            })
        elif action == "change_color":
            if shape_list:
                last_shape = shape_list[-1]
                hexcolor = request.form["new_color"]
                last_shape["color"] = hex_to_rgb(hexcolor)
        elif action == "move_shape":
            if shape_list:
                last_shape = shape_list[-1]
                last_shape["x"] = random.randint(50, 350)
                last_shape["y"] = random.randint(50, 350)

        # Redraw image with a new filename and update storage
        new_filename = f"art_{random.randint(1000,9999)}.png"
        create_image_from_shapes(shape_list, new_filename)

        old_path = os.path.join(ART_FOLDER, filename)
        if os.path.exists(old_path):
            os.remove(old_path)

        ART_DATA.pop(filename)
        ART_DATA[new_filename] = shape_list

        return redirect(url_for("edit_art", filename=new_filename))

    return render_template("edit_art.html", filename=filename)

@app.route("/download/<filename>")
def download_art(filename):
    return send_from_directory(ART_FOLDER, filename, as_attachment=True)

def hex_to_rgb(hexcolor):
    """Convert hexadecimal color #RRGGBB to tuple (R, G, B)."""
    r = int(hexcolor[1:3], 16)
    g = int(hexcolor[3:5], 16)
    b = int(hexcolor[5:7], 16)
    return (r, g, b)


# --------------------------------------------------------------
# 3. DATA VISUALIZATION ROUTE
# --------------------------------------------------------------

from data_visualizations.data_viz_logic import (
    load_weather_data,
    create_swirl_chart,
    # Import the new creative visualization functions:
    create_abstract_wave_chart,
    create_dynamic_bar_chart,
    create_temperature_heatmap
)


@app.route("/data_visualization", methods=["GET", "POST"])
def data_visualization():
    # 1. Load and sample data
    df = load_weather_data()
    df_sample = df.sample(10)
    table = df_sample.to_html(classes="data-table")
    stats = df.describe().to_html(classes="data-stats")
    statement = random.choice(STATEMENTS)

    # 2. Default chart URL is None
    chart_url = None

    # 3. Check if this is a POST request to generate a chart
    if request.method == "POST":
        # Which chart type did the user request?
        chart_type = request.form.get("chart_type", "swirl")  # default to swirl if not set

        # Generate a unique filename
        filename = f"{chart_type}_chart_{secrets.token_hex(4)}.png"
        output_path = os.path.join(IMAGES_FOLDER, filename)

        # 4. Call the corresponding function
        if chart_type == "swirl":
            create_swirl_chart(df, output_path)
        elif chart_type == "abstract_wave":
            create_abstract_wave_chart(df, output_path)
        elif chart_type == "dynamic_bar":
            create_dynamic_bar_chart(df, output_path)
        elif chart_type == "heatmap":
            create_temperature_heatmap(df, output_path)
        else:
            # Fallback to swirl or do nothing
            create_swirl_chart(df, output_path)

        # 5. Build the chart URL for display
        chart_url = url_for("static", filename=f"images/{filename}")

    # 6. Render the template
    return render_template(
        "data_viz.html",
        table=table,
        stats=stats,
        statement=statement,
        chart_url=chart_url
    )


# --------------------------------------------------------------
# 4. AUDIO ROUTES
# --------------------------------------------------------------
@app.route("/audio")
def audio_page():
    return render_template("audio.html")

@app.route("/generate_audio", methods=["GET"])
def generate_audio_route():
    try:
        buffer = generate_random_melody()
        return send_file(buffer, mimetype="audio/wav")
    except Exception as e:
        print("❌ Error generating audio:", e)
        return "Internal Server Error", 500

@app.route("/process_audio", methods=["POST"])
def process_audio():
    try:
        file = request.files.get("file")
        speed = float(request.form.get("speed", 1.0))
        if not file:
            return "Error: No audio file provided.", 400
        if speed <= 0:
            return "Error: Speed must be > 0.", 400

        buffer = change_audio_speed(file, speed)
        return send_file(buffer, mimetype="audio/wav")
    except Exception as e:
        print("❌ Error processing audio:", e)
        return "Internal Server Error", 500

@app.route("/merge_audio", methods=["POST"])
def merge_audio():
    try:
        file1 = request.files.get("file1")
        file2 = request.files.get("file2")
        if not file1 or not file2:
            return "Error: Two WAV files are required.", 400

        buffer = merge_audio_files(file1, file2)
        return send_file(buffer, mimetype="audio/wav")
    except Exception as e:
        print("❌ Error merging audio:", e)
        return "Internal Server Error", 500

# --------------------------------------------------------------
# 5. IMAGE MANIPULATION ROUTES
# --------------------------------------------------------------
@app.route("/image")
def image_page():
    return render_template("image.html")

@app.route("/apply_filter_ajax", methods=["POST"])
def apply_filter_ajax():
    if 'image' not in request.files:
        return jsonify(error="No file received."), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify(error="Empty file."), 400

    filter_name = request.form.get('filter', 'grayscale')
    input_path = os.path.join(IMAGES_FOLDER, file.filename)
    file.save(input_path)

    processed_filename = apply_filter(input_path, filter_name, IMAGES_FOLDER)
    return jsonify(filename=processed_filename)

# --------------------------------------------------------------
# 6. MACHINE LEARNING: TEXT GENERATION
# --------------------------------------------------------------
from ml_features.text_generation import generate_markov_text, generate_gpt2_text

@app.route("/text_gen", methods=["GET", "POST"])
def text_gen():
    generated_text = None
    model_choice = None

    if request.method == "POST":
        user_corpus = request.form.get("corpus_text", "")
        nb_sentences = int(request.form.get("nb_sentences", 3))
        model_choice = request.form.get("model_choice", "markov")

        if model_choice == "gpt2":
            prompt = user_corpus.strip() or "My artwork is beautiful."
            generated_text = generate_gpt2_text(prompt, max_length=50)
        else:
            generated_text = generate_markov_text(user_corpus, nb_sentences)

    return render_template("text_gen.html",
                           generated_text=generated_text,
                           model_choice=model_choice)

# --------------------------------------------------------------
# 7. DRAWING AND GALLERY ROUTES (PYGAME CANVAS)
# --------------------------------------------------------------
import pygame
import base64
from io import BytesIO
from datetime import datetime

# Artwork Manager for gallery
class ArtworkManager:
    def __init__(self):
        self.artworks = []
        self.load_artworks()

    def load_artworks(self):
        self.artworks.clear()
        for filename in os.listdir(GALLERY_FOLDER):
            if filename.endswith('.png'):
                filepath = os.path.join(GALLERY_FOLDER, filename)
                self.artworks.append({
                    'filename': filename,
                    'created_at': os.path.getctime(filepath),
                })
        self.artworks.sort(key=lambda x: x['created_at'], reverse=True)

    def save_artwork(self, image_data):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"artwork_{timestamp}.png"
        filepath = os.path.join(GALLERY_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(image_data))
        self.artworks.insert(0, {
            'filename': filename,
            'created_at': os.path.getctime(filepath)
        })
        return filename

# Drawing Canvas using Pygame
class DrawingCanvas:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.Surface((width, height))
        self.screen.fill((255, 255, 255))
        self.current_color = (0, 0, 0)
        self.drawing = False
        self.current_tool = "brush"
        self.brush_size = 5
        self.actions = []

    def handle_event(self, event_type, pos):
        if event_type == "mousedown":
            self.drawing = True
            self.draw_at_position(pos)
        elif event_type == "mousemove" and self.drawing:
            self.draw_at_position(pos)
        elif event_type == "mouseup":
            self.drawing = False
            self.actions.append(pygame.surfarray.array3d(self.screen))
        elif event_type == "undo" and self.actions:
            self.undo()
        elif event_type == "clear":
            self.clear()

    def draw_at_position(self, pos):
        if self.current_tool == "brush":
            pygame.draw.circle(self.screen, self.current_color, pos, self.brush_size)
        elif self.current_tool == "eraser":
            pygame.draw.circle(self.screen, (255, 255, 255), pos, self.brush_size * 2)
        elif self.current_tool == "square":
            rect = pygame.Rect(
                pos[0] - self.brush_size,
                pos[1] - self.brush_size,
                self.brush_size * 2,
                self.brush_size * 2
            )
            pygame.draw.rect(self.screen, self.current_color, rect)
        elif self.current_tool == "triangle":
            points = [
                (pos[0], pos[1] - self.brush_size * 2),
                (pos[0] - self.brush_size, pos[1] + self.brush_size),
                (pos[0] + self.brush_size, pos[1] + self.brush_size)
            ]
            pygame.draw.polygon(self.screen, self.current_color, points)
        elif self.current_tool == "rectangle":
            rect_width = self.brush_size * 3
            rect_height = self.brush_size * 2
            rect = pygame.Rect(
                pos[0] - rect_width // 2,
                pos[1] - rect_height // 2,
                rect_width,
                rect_height
            )
            pygame.draw.rect(self.screen, self.current_color, rect)
        elif self.current_tool == "star":
            import math
            center_x, center_y = pos
            outer_r = self.brush_size * 3
            inner_r = self.brush_size * 1.5
            star_points = []
            for i in range(10):
                angle = i * math.pi / 5
                r = outer_r if i % 2 == 0 else inner_r
                x = center_x + r * math.cos(angle)
                y = center_y + r * math.sin(angle)
                star_points.append((x, y))
            pygame.draw.polygon(self.screen, self.current_color, star_points)

    def undo(self):
        if self.actions:
            previous_state = self.actions.pop()
            pygame.surfarray.blit_array(self.screen, previous_state)

    def clear(self):
        self.screen.fill((255, 255, 255))
        self.actions = []

    def get_image_base64(self):
        image_io = BytesIO()
        pygame.image.save(self.screen, image_io, "PNG")
        image_io.seek(0)
        return base64.b64encode(image_io.getvalue()).decode()

canvas = DrawingCanvas()
artwork_manager = ArtworkManager()

@app.route('/draw')
def draw_page():
    return render_template('Draw.html')

@app.route('/gallery')
def gallery_page():
    displayed_artworks = []
    for art in artwork_manager.artworks:
        displayed_artworks.append({
            'filename': art['filename'],
            'created_at': art['created_at'],
            'path': url_for('static', filename=f'gallery/{art["filename"]}')
        })
    return render_template('Gallery.html', artworks=displayed_artworks)

@app.route('/api/draw', methods=['POST'])
def api_draw():
    data = request.json
    event_type = data.get('type')
    pos = tuple(map(int, data.get('pos', (0, 0))))
    canvas.handle_event(event_type, pos)
    return jsonify({'image': canvas.get_image_base64()})

@app.route('/api/save', methods=['POST'])
def api_save():
    image_data = canvas.get_image_base64()
    filename = artwork_manager.save_artwork(image_data)
    return jsonify({'success': True, 'filename': filename})

@app.route('/api/tool', methods=['POST'])
def api_change_tool():
    data = request.json
    canvas.current_tool = data.get('tool', 'brush')
    return jsonify({'success': True})

@app.route('/api/color', methods=['POST'])
def api_change_color():
    data = request.json
    color = data.get('color', '#000000')
    canvas.current_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    return jsonify({'success': True})

@app.route('/api/size', methods=['POST'])
def api_change_size():
    data = request.json
    canvas.brush_size = int(data.get('size', 5))
    return jsonify({'success': True})

@app.route('/download-current')
def download_current():
    image_data = canvas.get_image_base64()
    decoded = base64.b64decode(image_data)
    return send_file(
        io.BytesIO(decoded),
        mimetype='image/png',
        as_attachment=True,
        download_name='my_artwork.png'
    )

# --------------------------------------------------------------
# MAIN APPLICATION ENTRY POINT
# --------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
