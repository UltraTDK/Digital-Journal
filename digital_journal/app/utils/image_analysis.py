import streamlit as st # type: ignore
import numpy as np
import cv2
import os
from datetime import datetime
import mediapipe as mp # type: ignore

from tensorflow.keras.models import load_model # type: ignore

# Incarcarea modelului Fer
fer_model = load_model("models/fer_model.h5")
# Clasificarea emotiilor
emotion_labels_fer = ['Anger', 'Disgust', 'Fear', 'Happiness', 'Sadness', 'Surprise', 'Neutral']

# Incarcarea modelul de emotii pentru imagini folosind MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# ==================== Analiza imagine ==================== #
# Functie pentru detectie faciala haar_cascade
def detect_face_haar(image):
    # Conversie imaginea in tonuri de gri
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Initilizare haarcascade
    haarcascade_init = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detectarea fetelor din imagine
    faces = haarcascade_init.detectMultiScale(gray_image, 1.3, 5)
    
    if len(faces) == 0:
        return None, None
    else:
        # Este returnata prima fata detectata
        (x, y, w, h) = faces[0]
        face = image[y:y+h, x:x+w]
        return face

# Functie pentru detectie faciala mediapipe
def detect_face_mediapipe(image):
    # model_selection=1 - model cu precizie mai buna, dar mai lent, 
    # min_detection_confidence=0.5 - prob de 50% ca un obiect detectat sa fie o față
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        # Conversie din RGB in BGR pentru a putea folosi OpenCV
        bgr_img = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Este returnata prima fata detectata
        if bgr_img.detections:
            for detection in bgr_img.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = image.shape
                x = max(0, int(bboxC.xmin * iw))
                y = max(0, int(bboxC.ymin * ih))
                w = int(bboxC.width * iw)
                h = int(bboxC.height * ih)
                face = image[y:y+h, x:x+w]
                return face # Coordonatele feței detectate
    return None, None

def classify_emotion(face_image, model, emotion_labels):
    # Conversie imaginea in tonuri de gri
    face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

    # Redimensionare si normalizare pentru a putea fi clasificate
    face_image = cv2.resize(face_image, (48, 48))
    face_image = face_image.astype("float32") / 255.0
    face_image = np.expand_dims(face_image, axis=0)    # (1, 48, 48)
    face_image = np.expand_dims(face_image, axis=-1)   # (1, 48, 48, 1)

    # Predictie
    predictions = model.predict(face_image)[0]

    # Sortare indici si alegere 3 emotii dominante
    sorted_indices = predictions.argsort()[::-1]
    # 3 emotii, scorul cu 2 zecimale
    top_emotions = [(emotion_labels[i], round(float(predictions[i]) * 100, 2)) for i in sorted_indices[:3]]
    dominant_emotion = emotion_labels[sorted_indices[0]]

    return dominant_emotion, dict(top_emotions), predictions

# Functia principala
def analyze_face_emotion(
    img=None,
    image_path=None,
    face_det_method="haar",
    model_type="fer",
    emotion_labels=None,
    user_id=None
):
    # Incarcare imagine
    if img is None and image_path is not None:
        img = cv2.imread(image_path)
    if img is None:
        return "Invalid image.", {}, None, None

    # Detectie faciala
    if face_det_method == "haar":
        face = detect_face_haar(img)
        det_method_name = "HaarCascade"
    elif face_det_method == "mediapipe":
        face = detect_face_mediapipe(img)
        det_method_name = "MediaPipe"
    else:
        return "Invalid detection method.", {}, None, None

    st.markdown(f"The chosen method for facial detection: **{det_method_name}**")

    if face is None or not isinstance(face, np.ndarray):
        return "Face not detected.", {}, None, None
    
    # Selectarea modelului de clasificare
    model = fer_model

    if emotion_labels is None:
        return "Emotion labels are missing.", {}, None, None

    # Salvarea fetei detectate de mediapipe sau haar
    save_cropped_img_path = None
    if user_id and 'username' in st.session_state and st.session_state.username:
        # Creeaza folder pentru user
        user_dir = os.path.join("face_crops", st.session_state.username)
        os.makedirs(user_dir, exist_ok=True)

        # Formatul fisierului salvat: nume_data_ora
        timestamp = datetime.now().strftime("%Y.%m.%d_%H-%M-%S")
        filename = f"{st.session_state.username}_{timestamp}.jpg"
        save_cropped_img_path = os.path.join(user_dir, filename)

        # Salvare imaginii propriu-zise
        preview_face = cv2.resize(face, (200, 200))
        cv2.imwrite(save_cropped_img_path, preview_face)

    # Clasificare emotie
    dominant, scores, preds = classify_emotion(face, model, emotion_labels)

    return dominant, scores, preds, save_cropped_img_path