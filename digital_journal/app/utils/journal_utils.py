import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont # type: ignore
import streamlit as st # type: ignore

def save_journal_entry(user_id, text=None, text_emotion=None, image_emotion=None, image_path=None, title=None, timestamp=None):
    # Creare folder journal_pages daca nu exista
    user_dir = os.path.join("journal_pages", st.session_state.username)
    os.makedirs(user_dir, exist_ok=True)

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y.%m.d %H:%M")

    safe_timestamp = timestamp.replace(":", "-").replace(" ", "_")
    filename = f"journal_{safe_timestamp}.txt"
    full_journal_path_entry = os.path.join(user_dir, filename)

    with open(full_journal_path_entry, "w", encoding="utf-8") as f:
        # Data si ora
        f.write(f"*Date and time:* **{timestamp}**\n")
        # Titlu
        if title:
            f.write(f"*Title:* **{title}**\n")
        f.write("-" * 40 + "\n")
        # Textul jurnalului + emotia detectata in text
        if text:
            f.write("*Written text:*\n")
            f.write(text + "\n\n")
            f.write(f"*Emotion detected from text:* **{text_emotion}**\n\n")
        # Emotia detectata in imagine + fata detectata
        if image_emotion:
            f.write(f"*Emotion detected from image:* **{image_emotion}**\n")
            if image_path:
                f.write(f"Cropped image: {image_path}\n")
        f.write("-" * 40 + "\n")

    return full_journal_path_entry

def generate_journal_postcard(user_id, title, text, text_emotion, image_emotion=None, face_image_path=None, timestamp=None):
    # Dimensiuni imagine
    width, height = 800, 1000
    bg_color = "white"
    text_color = "black"

    # Fonturi
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 18)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Imagine de baza
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Data si ora
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y.%m.d %H:%M")
    draw.text((30, 20), f"Date and time: {timestamp}", fill=text_color, font=font_text)

    # Titlul
    if title:
        draw.text((30, 60), f"Title: {title}", fill=text_color, font=font_title)

    # Imagine
    if face_image_path and os.path.exists(face_image_path):
        try:
            face_img = Image.open(face_image_path)
            face_img = face_img.resize((150, 150))
            img.paste(face_img, (width - 180, 30))
            # if image_emotion:
            #     draw.text((width - 180, 190), f"{image_emotion}", fill=text_color, font=font_text)
        except Exception as error:
            print(f"Error loading image: {error}")

    # Textul jurnalului
    draw.text((30, 240), "Journal:", fill=text_color, font=font_title)

    # Impartirea textului pe linii ca sa nu iasa din postcard
    def wrap_text(text, font, max_width):
        lines = []
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    # Emotia din text
    lines = wrap_text(text, font_text, width - 60)
    y_text = 280
    for line in lines:
        draw.text((30, y_text), line, fill=text_color, font=font_text)
        y_text += 28

    draw.text((30, y_text + 20), f"Emotion detected from text: {text_emotion}", fill=text_color, font=font_text)
    y_text += 48 
    draw.text((30, y_text), f"Emotion detected from image: {image_emotion}", fill=text_color, font=font_text)

    # Salvare in folder utilizator
    user_dir = os.path.join("journal_postcards", st.session_state.username)
    os.makedirs(user_dir, exist_ok=True)

    safe_timestamp = timestamp.replace(":", "-").replace(" ", "_")
    filename = f"postcard_{safe_timestamp}.png"
    full_postcard_path = os.path.join(user_dir, filename)

    img.save(full_postcard_path)

    return full_postcard_path
