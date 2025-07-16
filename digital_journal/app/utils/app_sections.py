import streamlit as st # type: ignore
import pandas as pd # type: ignore
import sqlite3
import tempfile
import os

from datetime import datetime
from utils.image_analysis import analyze_face_emotion, emotion_labels_fer
from utils.text_analysis import analyze_text_emotion, analyze_text_emotion_bert
from utils.db_utils import save_emotion_to_db
from utils.recommendation import get_recommendation
from utils.journal_utils import save_journal_entry, generate_journal_postcard


# Modulul de analiza text
def _text_analysis():
    st.subheader("Emotional Analysis from Text")

    model_choice = st.radio("Choose the analysis model:", ["VADER", "BERT"], horizontal=True)

    user_input = st.text_area("Write what you feel:")

    if st.button("Analyze"):
        if user_input.strip():
            if model_choice == "VADER":
                emotion, top_emotions = analyze_text_emotion(user_input)
            else:
                emotion, top_emotions = analyze_text_emotion_bert(user_input)

            # Afisare rezultate
            st.success(f"*Detected emotion:* **{emotion}**")
            st.markdown(f"*Dominant emotions in text:*")
            for label, score in top_emotions:
                st.write(f"- **{label}**: {score}%")

            st.info(f"*Recommendation*: **{get_recommendation(emotion)}**")

            save_emotion_to_db(st.session_state.user_id, emotion, "text")

# Modulul de analiza imagine
def _image_analysis():
    st.subheader("Take a picture")

    with st.expander("Camera problems?"):
        st.markdown("""
        - If you have multiple cameras (e.g. laptop + USB webcam), the browser will use by default *the camera set in the system.
        - To change the camera used by the application:
        1. Click on LOCK in the browser address bar.
        2. Look for the CAMERA settings.
        3. Select the desired camera from the list.
        4. Click *Reload.
        """)

    # Alegerea metodei pentru detectie faciala
    fd_method = st.radio("Facial detection method:", ["HaarCascade", "MediaPipe"], horizontal=True)
    method_key = "haar" if fd_method == "HaarCascade" else "mediapipe"

    method_input = st.radio("Choose image upload method:", ["Camera", "Upload a file"], horizontal=True)

    # Reprezentarea pe coloane a preview-ului live si a rezultatelor
    col1, col2 = st.columns([2, 2])

    with col1:
        # Alegerea metodei pentru selfie
        image = None
        if method_input == "Camera":
            image = st.camera_input("Take a picture")
        elif method_input == "Upload a file":
            image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    with col2:
        if image:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(image.getbuffer())
                tmp_path = tmp.name

            # Afisarea rezultatelor
            st.markdown("**Results:**")
            st.image(tmp_path, caption="Uploaded Image", width=250)

            emotion, top_emotions, full_probs, img_path = analyze_face_emotion(
                image_path=tmp_path,
                face_det_method=method_key,
                model_type="fer",
                emotion_labels=emotion_labels_fer,
                user_id=st.session_state.get("user_id", None)
            )

            # Este afisata fata detectata
            if img_path:
                st.image(img_path, caption="Detected face", width=200)

            # Afisare emotie si recomandare
            if isinstance(emotion, str):
                st.success(f"Detected emotion: **{emotion}**")
                st.info(get_recommendation(emotion))

                # Alegerea celor 3 emotii dominante
                if isinstance(top_emotions, dict):
                    st.markdown("Dominant emotions:")
                    for label, score in top_emotions.items():
                        st.write(f"- {label}: {score}%")

                # Distributia completa a imaginilor sub forma de grafic
                if full_probs is not None and len(full_probs) == len(emotion_labels_fer):
                    chart_df = pd.DataFrame({
                        'Emotion': emotion_labels_fer,
                        'Probability (%)': [round(p * 100, 2) for p in full_probs]
                    })
                    st.markdown("Full distribution of emotions:")
                    st.bar_chart(chart_df.set_index("Emotion"))

                    save_emotion_to_db(st.session_state.user_id, emotion, f"image ({method_key})")
                else:
                    st.warning("The full distribution of emotions could not be generated.")
            else:
                st.warning(emotion)

# Pagina sub forma unui jurnal
def _journal_page():
    st.subheader("Emotional Journal Page")

     # Data si ora generate automat
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    time_str = now.strftime("%H:%M")

    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"**Date and time**: *{date_str}* *{time_str}*")
            title = st.text_input(f"**Page title** *(optional)*")
            
        with col2:
            camera_img = st.camera_input(f"**Take a selfie** *(optional)*")

    # Textul jurnalului 
    text_input = st.text_area(f"**Write your thoughts** *(required)*", height=250)

    if st.button("Analyze and save the log"):
        if not text_input.strip():
            st.warning("Please complete the diary text.")
            return

        # Initializare rezultate
        txt_emotion, img_emotion, img_path = None, None, None

        # Analiza text
        txt_emotion, _ = analyze_text_emotion_bert(text_input)
        st.success(f"*Emotion detected from text:* **{txt_emotion}**")
        st.info(f"*Recommendation:* **{get_recommendation(txt_emotion)}**")

        # Analiza imagine
        if camera_img:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(camera_img.getbuffer())
                tmp_path = tmp.name

            img_emotion, _, _, img_path = analyze_face_emotion(
                image_path=tmp_path,
                face_det_method="mediapipe",
                model_type="fer",
                emotion_labels=emotion_labels_fer,
                user_id=st.session_state.user_id
            )

            if img_emotion is None:
                st.warning(f"*No face detected in the image.*")
            else:
                st.success(f"*Emotion detected from the image:* **{img_emotion}**")
                st.info(f"*Recommendation:* **{get_recommendation(img_emotion)}**")
                if img_path:
                    st.image(img_path, caption="Detected Face", width=200)

        # Salvare in baza de date
        save_emotion_to_db(st.session_state.user_id, txt_emotion, "text")
        if img_emotion:
            save_emotion_to_db(st.session_state.user_id, img_emotion, "image")

        journal_path = save_journal_entry(
            user_id=st.session_state.user_id,
            text=text_input,
            text_emotion=txt_emotion,
            image_emotion=img_emotion,
            image_path=img_path,
            title=title,
            timestamp=now.strftime("%Y.%m.%d %H:%M")
        )

        # Este generat postcardul
        _ = generate_journal_postcard(
            user_id=st.session_state.user_id,
            title=title,
            text=text_input,
            text_emotion=txt_emotion,
            image_emotion=img_emotion,
            face_image_path=img_path,
            timestamp=now.strftime("%d.%m.%Y %H:%M")
        )

        # Vizualizare postcard
        with st.container():
            st.markdown("---")
            st.markdown("View saved log:")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"{date_str} {time_str}")
                if title:
                    st.markdown(f"{title}")
                st.markdown(f"Text:\n{text_input}")
                st.markdown(f"*Detected emotion from text:* **{txt_emotion}**")

            with col2:
                if img_path:
                    st.image(img_path, caption="Cropped image", width=150)
                    st.markdown(f"*Detected emotion from image:* **{img_emotion}**")

        st.success(f"Your diary has been saved! (`{journal_path}`)")
    
# Pagina cu rapoarte
def _emotional_report():
    st.subheader("Emotional Reports")

    # Selectare sectiune
    option = st.selectbox(
        "Choose the section:",
        ["Journal Pages", "Weekly Reports", "Daily Reports"]
    )

    if option == "Journal Pages":
        st.markdown("Scroll through the pages of the diary")

        postcard_dir = "journal_postcards"

        # Verificare daca exista folderul journal pages
        if not os.path.exists(postcard_dir):
            st.info("There are no saved journal pages.")
            return
    
        # Verificare daca exista folderul userului in journal pages
        user_dir = os.path.join(postcard_dir, st.session_state.username)
        if not os.path.exists(user_dir):
            st.info(f"No journal pages found for user **{st.session_state.username}**")
            return

        user_files = sorted([
            file for file in os.listdir(user_dir) if file.endswith(".png")
        ], reverse=True)

        if not user_files:
            st.info("There are no saved journal pages.")
        else:
            total_pages = len(user_files)

            if "journal_page_index" not in st.session_state:
                st.session_state.journal_page_index = 0

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Previous page"):
                    if st.session_state.journal_page_index > 0:
                        st.session_state.journal_page_index -= 1
            with col2:
                if st.button("Next page"):
                    if st.session_state.journal_page_index < total_pages - 1:
                        st.session_state.journal_page_index += 1

            # Afisare pagina curenta
            current_index = st.session_state.journal_page_index
            selected_file = user_files[current_index]
            image_path = os.path.join(user_dir, selected_file)

            st.image(image_path, caption=f"Page {current_index + 1} of {total_pages}", width=500)

            with open(image_path, "rb") as file:
                st.download_button("Download page", file, file_name=selected_file, mime="image/png")

    else:
        # Emotii din baza de date
        conn = sqlite3.connect("database.db")
        df = pd.read_sql_query("""
            SELECT timestamp, emotion, source FROM emotions
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, conn, params=(st.session_state.user_id,))
        conn.close()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['week'] = df['timestamp'].dt.isocalendar().week
            df['year'] = df['timestamp'].dt.isocalendar().year
            weeks = df[['year', 'week']].drop_duplicates().sort_values(['year', 'week'], ascending=False)

            if option == "Weekly Reports":
                selected_week = st.selectbox(
                    "Choose a week:",
                    [f"{row.year}-S{str(row.week).zfill(2)}" for _, row in weeks.iterrows()]
                )

                # Filtrare date
                selected_year, selected_w = selected_week.split("-S")
                selected_w = int(selected_w)
                selected_year = int(selected_year)

                week_data = df[
                    (df['year'] == selected_year) & (df['week'] == selected_w)
                ]

                if not week_data.empty:
                    st.markdown(f"**Emotions during the week:** *{selected_week}*")
                    emotion_counts = week_data["emotion"].value_counts()
                    st.bar_chart(emotion_counts)

                    dominant = emotion_counts.idxmax()
                    emoji_map = {
                        "Hapiness": "😄",
                        "Sadness": "😢",
                        "Anger": "😠",
                        "Fear": "😨",
                        "Neutral": "😐",
                        "Disgust": "🤢",
                        "Surprise": "😲"
                    }
                    emoji = emoji_map.get(dominant, "")
                    recommendation = get_recommendation(dominant)

                    st.markdown(f"*Dominant emotion*: `{dominant}` {emoji}")
                    st.info(f"*Recommendation for this week:*\n\n**{recommendation}**")
                else:
                    st.info("There are no data for this week.")

                st.dataframe(df)

            if option == "Daily Reports":
                st.markdown("Daily Reports")
                st.line_chart(df.groupby("date")["emotion"].count())

                selected_day = st.selectbox("Choose the day:", sorted(df['date'].unique(), reverse=True))
                day_data = df[df['date'] == selected_day]["emotion"].value_counts()
                st.bar_chart(day_data)

        else:
            st.info("There are no emotions saved.")
