from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # type: ignore
from deep_translator import GoogleTranslator # type: ignore
from transformers import pipeline # type: ignore
from langdetect import detect # type: ignore

# ==================== Analiza text ==================== #
# Traducere text inainte de a fi analizat
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

# Analiza text Vader
def analyze_text_emotion(text):
    # Traducerea textului în engleza
    analyzer = SentimentIntensityAnalyzer()

    # Este analizat doar textul tradus
    translated = translate_to_english(text)
    scores = analyzer.polarity_scores(translated)

    emotion_scores = {
        "Happiness": scores['pos'],
        "Sadness": scores['neg'],
        "Neutral": scores['neu']
    }

    # Clasificarea emotiei in functie de scor
    # Contine in plus anger fata de varianta clasica
    # emotion_scores = {
    #     "Happiness": scores['pos'],
    #     "Sadness": abs(scores['neg']) if scores['compound'] < -0.3 else 0,
    #     "Anger": scores['neg'] if scores['neg'] > 0.3 else 0,
    #     "Neutral": scores['neu']
    # }

    # Ordonarea emotiilor detectate
    sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Alegere top 3 emotii descrescator 
    top_three_emotions = [(label, round(score * 100, 2)) for label, score in sorted_emotions if score > 0]

    # Emotia dominanta are cel mai mare scor pozitiv
    main_emotion = top_three_emotions[0][0] if top_three_emotions else "Neutral"

    return main_emotion, top_three_emotions

# Inițializare model BERT
emotion_classifier = pipeline("text-classification", 
                              model="j-hartmann/emotion-english-distilroberta-base", 
                              top_k=None)

emotion_labels = {
"joy": "Happiness",
"sadness": "Sadness",
"anger": "Anger",
"fear": "Fear",
"disgust": "Disgust",
"surprise": "Surprise",
"neutral": "Neutral"
}

# Analiza text Bert 
def analyze_text_emotion_bert(text):
     # Detectare limba
    try:
        detected_lang = detect(text)
    except:
        detected_lang = 'en'

    # Traducere doar daca limba detectata nu este engleza
    if detected_lang != 'en':
        text_en = GoogleTranslator(source='auto', target='en').translate(text)
    else:
        text_en = text

    # Clasificare emotie
    predictions = emotion_classifier(text_en)[0]

    # Sortarea emotii
    preds_sorted = sorted(predictions, key=lambda x: x['score'], reverse=True)

    # Emotia dominanta si top 3 emotii
    dominant_emotion = preds_sorted[0]['label']
    top_emotion = emotion_labels[dominant_emotion]
    
    top_3 = [(emotion_labels[p['label']], round(p['score'] * 100, 2)) for p in preds_sorted[:3]]

    return top_emotion, top_3
