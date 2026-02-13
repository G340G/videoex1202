#!/usr/bin/env python3
"""
SEPHIROTH V10 — AUTONOMOUS SIGNAL SYSTEM
GitHub-Optimized Edition
NO pyttsx3
Uses espeak directly
Guaranteed audio mux
Fully chaotic analog corruption
"""

import os
import random
import subprocess
import requests
import numpy as np
import tempfile
import shutil
import uuid
from PIL import Image, ImageDraw, ImageFont

# ============================
# CONFIG
# ============================

WIDTH = 720
HEIGHT = 480
FPS = 30
DURATION = random.randint(60, 120)
OUTPUT_FORMAT = "mov"

WORK = tempfile.mkdtemp(prefix="SEPHIROTH_V10_")
FRAMES = os.path.join(WORK, "frames")
os.makedirs(FRAMES, exist_ok=True)

# ============================
# AUTONOMOUS BRAIN
# ============================

def load_keywords():
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/dwyl/english-words/master/words.txt",
            timeout=10)
        words = r.text.splitlines()
        return words[:20000]
    except:
        return ["signal", "void", "entity", "collapse", "infection"]

KEYWORDS = load_keywords()
KEYWORD = random.choice(KEYWORDS)
print("KEYWORD:", KEYWORD)

# ============================
# TEXT SCRAPER
# ============================

def scrape_text(keyword):
    texts = []
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{keyword}",
            timeout=10)
        if r.status_code == 200:
            texts.append(r.json().get("extract", ""))
    except:
        pass

    texts += [
        f"ENTITY DETECTED: {keyword.upper()}",
        "THIS IS NOT A TEST",
        "SIGNAL CONTAMINATION",
        "DO NOT LOOK DIRECTLY",
        "THE BROADCAST IS ALIVE",
        "TRANSMISSION OVERRIDE"
    ]

    return texts

TEXTS = scrape_text(KEYWORD)

# ============================
# IMAGE GENERATOR (NO 404s)
# ============================

def generate_image_variants(count=40):
    paths = []

    for i in range(count):
        img = Image.new("RGB", (WIDTH, HEIGHT), (
            random.randint(0,30),
            random.randint(0,30),
            random.randint(0,30)
        ))

        draw = ImageDraw.Draw(img)

        # chaotic shapes
        for _ in range(random.randint(20, 60)):
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            x2 = random.randint(0, WIDTH)
            y2 = random.randint(0, HEIGHT)
            draw.line((x1,y1,x2,y2),
                      fill=(random.randint(100,255),0,0),
                      width=random.randint(1,3))

        path = os.path.join(WORK, f"img_{i}.png")
        img.save(path)
        paths.append(path)

    return paths

IMAGES = generate_image_variants()

# ============================
# ANALOG CORRUPTION
# ============================

def analog_corrupt(img):
    arr = np.array(img)
    noise = np.random.randint(0,50,arr.shape,dtype=np.uint8)
    arr = np.clip(arr + noise,0,255)

    # horizontal shift glitch
    if random.random() < 0.3:
        shift = random.randint(-50,50)
        arr = np.roll(arr, shift, axis=1)

    return Image.fromarray(arr)

# ============================
# FRAME GENERATOR
# ============================

font = ImageFont.load_default()

def make_frame(i):
    base = Image.new("RGB",(WIDTH,HEIGHT),(0,0,0))
    draw = ImageDraw.Draw(base)

    # multiple layers
    for _ in range(random.randint(1,4)):
        img_path = random.choice(IMAGES)
        im = Image.open(img_path)
        im = im.resize((random.randint(200,WIDTH),
                        random.randint(200,HEIGHT)))
        base.paste(im,
                   (random.randint(0, WIDTH-200),
                    random.randint(0, HEIGHT-200)))

    # text overlays
    for _ in range(random.randint(1,6)):
        text = random.choice(TEXTS)
        draw.text(
            (random.randint(0, WIDTH-200),
             random.randint(0, HEIGHT-20)),
            text,
            fill=(255, random.randint(0,50), random.randint(0,50)),
            font=font
        )

    # jumpscare flash
    if random.random() < 0.015:
        draw.rectangle((0,0,WIDTH,HEIGHT), fill=(255,255,255))
        draw.text((WIDTH//2, HEIGHT//2),
                  "LOOK AWAY",
                  fill=(0,0,0),
                  font=font)

    base = analog_corrupt(base)
    base.save(f"{FRAMES}/frame_{i:06d}.png")

print("Generating frames...")
for i in range(DURATION * FPS):
    make_frame(i)

# ============================
# AUDIO GENERATION
# ============================

def generate_tts(text):
    wav_file = os.path.join(WORK, f"tts_{uuid.uuid4().hex}.wav")

    subprocess.run([
        "espeak",
        "-v", "en",
        "-s", "120",
        "-p", "40",
        "-w", wav_file,
        text
    ], check=True)

    return wav_file

tts_file = generate_tts(
    f"WARNING. SIGNAL CONTAMINATION DETECTED. ENTITY NAME: {KEYWORD}"
)

# background noise
noise_file = os.path.join(WORK, "noise.wav")

subprocess.run([
    "ffmpeg",
    "-y",
    "-f","lavfi",
    "-i",f"anoisesrc=color=pink:duration={DURATION}",
    noise_file
], check=True)

# mix audio
final_audio = os.path.join(WORK, "final_audio.wav")

subprocess.run([
    "ffmpeg",
    "-y",
    "-i", noise_file,
    "-i", tts_file,
    "-filter_complex","amix=inputs=2",
    final_audio
], check=True)

# ============================
# VIDEO EXPORT (GUARANTEED AUDIO)
# ============================

OUTPUT = f"SEPHIROTH_V10_{KEYWORD}.{OUTPUT_FORMAT}"

subprocess.run([
    "ffmpeg",
    "-y",
    "-framerate", str(FPS),
    "-i", f"{FRAMES}/frame_%06d.png",
    "-i", final_audio,
    "-c:v","mpeg4",
    "-q:v","3",
    "-c:a","aac",
    "-shortest",
    OUTPUT
], check=True)

print("CREATED:", OUTPUT)

shutil.rmtree(WORK)

