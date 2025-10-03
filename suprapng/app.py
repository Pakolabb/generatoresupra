import streamlit as st
from PIL import Image
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cartelle parti variabili
folders = {
    "Tetto": "tetto",
    "Cofano": "cofano",
    "Carrozzeria": "carrozzeria",
    "Pinze": "pinza",
    "Cerchioni": "cerchioni",
}

# File fissi (ordine livelli)
fixed_files = [
    "gomme.png",       # sotto a tutti
    "ombra.png",
    "logoopacita.png",
    "dettagli.png"
]

# Probabilità colori
color_probs = {
    "base": 0.83,
    "turchese": 0.07,
    "viola": 0.05,
    "cf": 0.04,
    "gold": 0.01
}

def choose_color(files):
    """Sceglie un file in base alle probabilità definite"""
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

st.title("Generatore Supra 🎨")

if st.button("Genera Auto"):
    canvas = None
    report = {}  # per salvare i colori usciti

    # Parti variabili (con probabilità)
    for part, folder in folders.items():
        part_folder = os.path.join(BASE_DIR, folder)
        if os.path.exists(part_folder):
            files = os.listdir(part_folder)
            if files:
                chosen = choose_color(files)
                img = Image.open(os.path.join(part_folder, chosen)).convert("RGBA")
                if canvas is None:
                    canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))
                canvas.alpha_composite(img)

                # salvo il nome colore per il report
                report[part] = os.path.splitext(chosen)[0]

    # File fissi
    for fname in fixed_files:
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.exists(fpath):
            img = Image.open(fpath).convert("RGBA")
            canvas.alpha_composite(img)

    if canvas:
        st.image(canvas, caption="La tua Supra generata", use_container_width=True)

        # Mostra il report
        st.subheader("Dettagli generazione:")
        for part, colore in report.items():
            st.write(f"**{part}** → {colore}")
    else:
        st.write("Nessuna immagine trovata!")
