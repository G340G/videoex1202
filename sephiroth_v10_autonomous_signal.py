#!/usr/bin/env python3
"""
SEPHIROTH V10 LO-FI EDITION
GitHub optimized
Small file size
Full features preserved
Analog horror aesthetic
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

# ======================
# LO-FI CONFIG (CRITICAL)
# ======================

WIDTH = 360      # was 720
HEIGHT = 240     # was 480
FPS = 12         # was 30
DURATION = random.randint(35, 55)

CRF = "32"       # compression (lower = bigger, higher = smaller)
PRESET = "veryfast"

WORK = tempfile.mkdtemp(prefix="SEPHIROTH_LOFI_")
FRAMES = os.path.join(WORK, "frames")

os.makedirs(FRAMES, exist_ok=True)

# ======================
# KEYWORD BRAIN
# ======================

def load_keywords():
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/dwyl/english-words/master/words.txt",
            timeout=10)
        return r.text.splitlines()[:15000]
    except:
        return ["entity","signal","void","collapse"]

KEYWORD = random.choice(load_keywords())
print("KEYWORD:", KEYWORD)

# ======================
# TEXT SCRAPER
# ======================

def scrape():
    t = []

    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{KEYWORD}",
            timeout=5)

        if r.status_code == 200:
            t.append(r.json().get("extract",""))
    except:
        pass

    t += [
        "EMERGENCY BROADCAST SYSTEM",
        "THIS IS NOT A TEST",
        f"ENTITY CLASS: {KEYWORD.upper()}",
        "SIGNAL CONTAMINATION",
        "DO NOT RESPOND",
        "OBSERVATION ACTIVE",
        "THEY CAN SEE YOU"
    ]

    return t

TEXTS = scrape()

# ======================
# IMAGE GENERATOR
# ======================

def make_images(n=25):

    paths=[]

    for i in range(n):

        img = Image.new("L",(WIDTH,HEIGHT),
            random.randint(0,40))

        draw = ImageDraw.Draw(img)

        for _ in range(random.randint(10,30)):
            draw.line(
                (
                    random.randint(0,WIDTH),
                    random.randint(0,HEIGHT),
                    random.randint(0,WIDTH),
                    random.randint(0,HEIGHT)
                ),
                fill=random.randint(100,255),
                width=1
            )

        p = os.path.join(WORK,f"img{i}.png")

        img.save(p)

        paths.append(p)

    return paths

IMAGES = make_images()

# ======================
# ANALOG DAMAGE
# ======================

def corrupt(im):

    arr = np.array(im)

    noise = np.random.randint(
        0,40,arr.shape,dtype=np.uint8)

    arr = np.clip(arr+noise,0,255)

    if random.random()<0.25:

        shift=random.randint(-20,20)

        arr=np.roll(arr,shift,axis=1)

    return Image.fromarray(arr)

# ======================
# FRAME GENERATOR
# ======================

font = ImageFont.load_default()

def frame(i):

    base = Image.new(
        "L",
        (WIDTH,HEIGHT),
        random.randint(0,30)
    )

    draw = ImageDraw.Draw(base)

    # image layers
    for _ in range(random.randint(1,3)):

        im = Image.open(
            random.choice(IMAGES))

        base.paste(
            im,
            (
                random.randint(0,WIDTH-50),
                random.randint(0,HEIGHT-50)
            )
        )

    # text layers
    for _ in range(random.randint(1,4)):

        draw.text(

            (
                random.randint(0,WIDTH-100),
                random.randint(0,HEIGHT-10)
            ),

            random.choice(TEXTS),

            fill=random.randint(150,255),

            font=font
        )

    # jumpscare
    if random.random()<0.02:

        draw.rectangle(
            (0,0,WIDTH,HEIGHT),
            fill=255
        )

        draw.text(
            (WIDTH//3,HEIGHT//2),
            "LOOK AWAY",
            fill=0,
            font=font
        )

    base = corrupt(base)

    base.save(
        f"{FRAMES}/frame_{i:05d}.png"
    )

print("Generating frames...")

for i in range(DURATION*FPS):

    frame(i)

# ======================
# AUDIO
# ======================

def tts():

    f=os.path.join(
        WORK,
        f"tts_{uuid.uuid4().hex}.wav"
    )

    subprocess.run([

        "espeak",

        "-v","en",

        "-s","110",

        "-p","40",

        "-w",f,

        f"WARNING. ENTITY {KEYWORD}. SIGNAL CONTAMINATED."

    ])

    return f

tts_file=tts()

noise=os.path.join(WORK,"noise.wav")

subprocess.run([

    "ffmpeg","-y",

    "-f","lavfi",

    "-i",f"anoisesrc=color=pink:duration={DURATION}",

    noise

])

audio=os.path.join(WORK,"audio.wav")

subprocess.run([

    "ffmpeg","-y",

    "-i",noise,

    "-i",tts_file,

    "-filter_complex","amix=inputs=2",

    audio

])

# ======================
# EXPORT (SMALL SIZE)
# ======================

OUTPUT=f"SEPHIROTH_V10_LOFI_{KEYWORD}.mov"

subprocess.run([

    "ffmpeg",

    "-y",

    "-framerate",str(FPS),

    "-i",f"{FRAMES}/frame_%05d.png",

    "-i",audio,

    "-c:v","libx264",

    "-preset",PRESET,

    "-crf",CRF,

    "-pix_fmt","yuv420p",

    "-c:a","aac",

    "-b:a","64k",

    "-shortest",

    OUTPUT

])

print("CREATED:",OUTPUT)

shutil.rmtree(WORK)


