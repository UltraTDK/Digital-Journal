import numpy as np
import mediapipe as mp # type: ignore
import sqlite3
import os

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # type: ignore
from deep_translator import GoogleTranslator # type: ignore
from tensorflow.keras.models import load_model # type: ignore
from transformers import pipeline # type: ignore

# Incarcarea modelul de emotii pentru imagini folosind Fer2013
fer_model = load_model("models/fer_model.h5")

def check_system_status():
    status = {}

    # Verificare Fer Model
    try:
        _ = fer_model.predict(np.zeros((1, 48, 48, 1)))
        status['Model Emoție (Imagine)'] = True
    except Exception:
        status['Model Emoție (Imagine)'] = False

    # Verificare MediaPipe
    try:
        _ = mp.solutions.face_detection.FaceDetection()
        status['MediaPipe (Face Detection)'] = True
    except:
        status['MediaPipe (Face Detection)'] = False

    # Verificare bază de date
    try:
        conn = sqlite3.connect("database.db")
        conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        conn.close()
        status['Baza de date'] = True
    except:
        status['Baza de date'] = False

    folders = ["journal_pages", "journal_postcards", "face_crops"]
    for folder in folders:
        status[f'Folder "{folder}" existent'] = os.path.exists(folder)

    # Verificare VADER
    try:
        SentimentIntensityAnalyzer()
        status['VADER (Text)'] = True
    except:
        status['VADER (Text)'] = False

    # Verificare Bert
    try:
        _ = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
        status['Model Emoție (Text - BERT)'] = True
    except:
        status['Model Emoție (Text - BERT)'] = False

    # Verificare traducere
    try:
        _ = GoogleTranslator(source='auto', target='en').translate("test")
        status['Traducere automată'] = True
    except:
        status['Traducere automată'] = False

    return status