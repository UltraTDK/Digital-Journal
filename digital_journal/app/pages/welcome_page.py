import streamlit as st # type: ignore
import os

from utils.image_analysis import analyze_face_emotion, emotion_labels_fer
from utils.text_analysis import analyze_text_emotion_bert
from utils.recommendation import get_recommendation

def show():
    st.title("👋 Welcome to the Digital Journal App!")

    st.subheader("What does the application offer:")
    st.markdown("""
        - Text analysis – write what you feel and receive an emotional analysis
        - Image analysis – the camera reads your facial expression
        - Journal – write how you felt today
        - Reports – analyze your emotional evolution over time
    """)

    st.subheader("Demo of the application:")

    st.markdown("1. Preview of text analysis:")
    user_input = st.text_area("Write something...", key="demo_text")
    if st.button("Analyze the text"):
        if user_input.strip():
            emotion, top_emotions = analyze_text_emotion_bert(user_input)
            st.markdown(f"Emotion detected: **{emotion}**")
            for label, score in top_emotions:
                st.markdown(f"– {label}: {score}%")
            st.info(get_recommendation(emotion))

    st.markdown("2. Preview of the image analysis:")
    method = st.radio("Choose image upload method:", ["Camera", "Upload a file"], horizontal=True)

    # Reprezentarea pe coloane a preview-ului live si a rezultatelor
    col1, col2 = st.columns([2, 2])

    with col1:
        # Alegerea metodei pentru selfie
        image = None
        if method == "Camera":
            image = st.camera_input("Take a picture", key="demo_cam")
        elif method == "Upload a file":
            image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="upload_demo")

    with col2:
        if image:
            with open("temp_image.jpg", "wb") as f:
                f.write(image.getbuffer())

            st.markdown(f"**Results:**")
            st.image("temp_image.jpg", caption="Uploaded Image", width=250)

            emotion, top_emotions, _, _ = analyze_face_emotion(
                image_path="temp_image.jpg",
                face_det_method="mediapipe",
                model_type="fer",
                emotion_labels=emotion_labels_fer,
                user_id=None
            )

            if os.path.exists("temp_image.jpg"):
                os.remove("temp_image.jpg")

            st.markdown(f"Detected emotion: **{emotion}**")
            for label, score in top_emotions.items():
                st.markdown(f"– *{label}*: **{score}**%")
            st.info(get_recommendation(emotion))

    st.markdown("""
    ---
    To enjoy all the functionalities offered by the application, please log in.
    """)
