import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from PIL.Image import Resampling
import os
import random
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Contatore globale
def get_generation_count():
    counter_path = os.path.join(BASE_DIR, "counter.txt")
    if not os.path.exists(counter_path):
        with open(counter_path, "w") as f:
            f.write("0")
    with open(counter_path, "r") as f:
        try:
            count = int(f.read().strip())
        except:
            count = 0
    return count

def increment_generation_count():
    counter_path = os.path.join(BASE_DIR, "counter.txt")
    count = get_generation_count() + 1
    with open(counter_path, "w") as f:
        f.write(str(count))
    return count

folders = {
    "Tetto": "tetto",
    "Cofano": "cofano",
    "Carrozzeria": "carrozzeria",
    "Pinze": "pinza",
    "Cerchioni": "cerchioni",
}

fixed_files = [
    "gomme.png",
    "ombra.png",
    "dettagli.png"
]

logo_file = "Logoopacita1.png"

color_probs = {
    "base": 0.83,
    "turchese": 0.07,
    "viola": 0.05,
    "cf": 0.04,
    "gold": 0.01
}

def choose_color(files):
    base_colors = [f for f in files if not any(x in f.lower() for x in ["turchese", "viola", "cf", "gold"])]
    turchese = [f for f in files if "turchese" in f.lower()]
    viola = [f for f in files if "viola" in f.lower()]
    cf = [f for f in files if "cf" in f.lower() or "fibra" in f.lower()]
    gold = [f for f in files if "gold" in f.lower()]

    choices, weights = [], []
    if base_colors:
        choices.append(random.choice(base_colors))
        weights.append(color_probs["base"])
    if turchese:
        choices.append(random.choice(turchese))
        weights.append(color_probs["turchese"])
    if viola:
        choices.append(random.choice(viola))
        weights.append(color_probs["viola"])
    if cf:
        choices.append(random.choice(cf))
        weights.append(color_probs["cf"])
    if gold:
        choices.append(random.choice(gold))
        weights.append(color_probs["gold"])

    return random.choices(choices, weights=weights, k=1)[0]

def apply_logo(canvas, logo_path):
    logo_img = Image.open(logo_path).convert("RGBA")
    canvas_w, canvas_h = canvas.size
    logo_w, logo_h = logo_img.size
    ratio = min(canvas_w / logo_w, canvas_h / logo_h) * 0.5
    new_size = (int(logo_w * ratio), int(logo_h * ratio))
    logo_img = logo_img.resize(new_size, Resampling.LANCZOS)

    layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    x = (canvas_w - new_size[0]) // 2
    y = (canvas_h - new_size[1]) // 2
    layer.paste(logo_img, (x, y), logo_img)
    canvas.alpha_composite(layer)

def apply_glow(image, intensity=1.6, blur_radius=12):
    blurred = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    enhancer = ImageEnhance.Brightness(blurred)
    glow = enhancer.enhance(intensity)
    glow.paste(image, (0, 0), image)
    return glow

def apply_shadow(base_size, shadow_path, offset=(0, 30), blur_radius=6):
    shadow = Image.open(shadow_path).convert("RGBA")
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    layer = Image.new("RGBA", base_size, (255, 255, 255, 0))
    layer.paste(shadow, offset, shadow)
    return layer

def add_glow_frame(canvas, color, thickness=12, blur_radius=8, intensity=1.5):
    w, h = canvas.size
    frame = Image.new("RGBA", (w + thickness*2, h + thickness*2), (0, 0, 0, 0))
    frame.paste(canvas, (thickness, thickness), canvas)

    glow_layer = Image.new("RGBA", frame.size, color + (255,))
    mask = Image.new("L", frame.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle([0, 0, frame.size[0], frame.size[1]], outline=255, width=thickness)

    glow_layer.putalpha(mask)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    enhancer = ImageEnhance.Brightness(glow_layer)
    glow_layer = enhancer.enhance(intensity)

    frame.alpha_composite(glow_layer)
    return frame

def create_background(size, base_color):
    r, g, b = base_color
    light_color = (min(r + 100, 255), min(g + 100, 255), min(b + 100, 255))
    bg = Image.new("RGBA", size, light_color + (255,))
    return bg

def add_signature(image, text="@pakolabb", y_offset=40):
    draw = ImageDraw.Draw(image)
    font_size = int(image.width * 0.06)
    try:
        font_path = os.path.join(BASE_DIR, "arial.ttf")
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (image.width - text_width) // 2
    y = y_offset
    draw.text((x, y), text, font=font, fill=(0, 0, 0, 200))
    return image

# Interfaccia
st.title("Generatore Supra ✨")
current_count = get_generation_count()
st.markdown(f"**🚗 Generazioni totali effettuate: `{current_count}`**")

if st.button("Genera Auto"):
    canvas = None
    report = {}
    carrozzeria_img = None

    for part, folder in folders.items():
        part_folder = os.path.join(BASE_DIR, folder)
        if os.path.exists(part_folder):
            files = [f for f in os.listdir(part_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if files:
                chosen = choose_color(files)
                try:
                    img = Image.open(os.path.join(part_folder, chosen)).convert("RGBA")
                    if canvas is None:
                        canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))
                    canvas.alpha_composite(img)
                    report[part] = os.path.splitext(chosen)[0]
                    if part == "Carrozzeria":
                        carrozzeria_img = img.copy()
                except Exception as e:
                    st.warning(f"Errore nel caricamento di {chosen}: {e}")

    for f in fixed_files:
        fpath = os.path.join(BASE_DIR, f)
        if os.path.exists(fpath) and f != "ombra.png":
            img = Image.open(fpath).convert("RGBA")
            canvas.alpha_composite(img)

    if canvas and carrozzeria_img:
        shadow_path = os.path.join(BASE_DIR, "ombra.png")
        logo_path = os.path.join(BASE_DIR, logo_file)

        auto_layer = apply_glow(canvas.copy(), intensity=1.6, blur_radius=12)
        shadow_layer = apply_shadow(canvas.size, shadow_path, offset=(0, 30), blur_radius=6)
        shadow_layer.alpha_composite(auto_layer)
        apply_logo(shadow_layer, logo_path)

        dominant_color = carrozzeria_img.resize((1, 1)).getpixel((0, 0))[:3]
        bg = create_background(shadow_layer.size, dominant_color)
        bg.alpha_composite(shadow_layer)

        final_image = add_glow_frame(bg, dominant_color)
        final_image = add_signature(final_image, "@pakolabb", y_offset=40)

        st.image(final_image, caption="La tua Supra personalizzata", use_container_width=True)

        buffer = io.BytesIO()
        final_image.save(buffer, format="PNG")
    st.download_button("📥 Salva immagine", data=buffer.getvalue(), file_name="supra_pakolabb.png", mime="image/png")
