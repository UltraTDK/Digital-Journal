import random

def get_recommendation(emotion):
    recommendations = {
        "Happiness": [
            "Keep up your positive mood! Maybe share your joy with someone close.",
            "You're on the right track! Spread your positive energy to those around you.",
            "Enjoy this feeling! A creative activity might bring you even more satisfaction."
        ],
        "Sadness": [
            "Try to get some rest or talk to someone you care about. A walk might help.",
            "It's okay to feel this way. A break or a hobby might help lift your spirits.",
            "Try focusing on your breathing or doing something that brings you peace."
        ],
        "Anger": [
            "Take a deep breath. Try taking a break or doing some light physical activity to calm down.",
            "A brisk walk might help release the tension.",
            "Take time for a relaxing activity or talk to someone about what's frustrating you."
        ],
        "Fear": [
            "Try identifying the source of your fear and talk to someone you trust.",
            "Fear can sometimes be a signal. What could you do to feel safer?",
            "Reflect on your fear and see if there’s a way to face it step by step."
        ],
        "Neutral": [
            "A balanced day is a good day. You might reflect on what could bring you joy today.",
            "Maybe you just need a moment to relax or engage in a hobby to recharge.",
            "What could you do today to improve your well-being?"
        ],
        "Disgust": [
            "Maybe it’s time to distance yourself from something that’s not serving you. Focus on what you enjoy.",
            "Take time to recharge with activities that bring you pleasure.",
            "Find something that shifts your perspective and helps you feel better."
        ],
        "Surprise": [
            "Something unexpected? Write it down and reflect on how it made you feel.",
            "When faced with the unexpected, it's a great time to explore new possibilities.",
            "What did you learn from this surprise, and how do you feel about it now?"
        ]
    }

    # Alegerea in mod aleatoriu a unei recomandari
    return random.choice(recommendations.get(emotion, ["The detected emotion does not have an associated recommendation (yet)."]))
