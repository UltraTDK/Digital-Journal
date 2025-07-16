# Digital-Journal
This my Bachelor Degree Application that is designed as a personal emotional journal.

## Installation

Run the following command in CMD to install all required libraries:

```bash
pip install -r requirements.txt
```

```bash
pip install .\tensorflow-2.19.0-cp311-cp311-win_amd64.whl
```

> Note: Due to issues encountered while installing TensorFlow, it was faster to install it from a local file, unfortunately i couldn't upload it on GitHub.

The application was developed using **Python 3.11.8**, which is the only version compatible with the latest TensorFlow library update.

---

## Application Features

### Authentication and Registration

- Users can create accounts and log in.
- Authenticated users can save their emotional analyses and generate reports.

### Main Page

#### Text Analysis

- Returns the top 3 dominant emotions.
- Analysis is performed using a pre-trained BERT model:  
  [`j-hartmann/emotion-english-distilroberta-base`](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base)
- Input text is automatically translated into English using `deep-translator`.

#### Image Analysis

- Returns the top 3 dominant emotions based on facial expressions.
- Uses pre-trained models on the FER dataset (e.g., MediaPipe or HaarCascade).

### Emotional Journal Page

- Users can write a journal entry and optionally upload a selfie.
- The analysis result is saved and displayed as a visual postcard, styled like a journal page.

### Reports Page

- Provides weekly and daily emotion reports.
- Displays data in graphical form, along with recommendations based on the dominant emotion.

### Demo Page (No Login Required)

- Allows unregistered users to test the text and image analysis functionalities quickly.

---

## Running the Application

Navigate to the `Digital-Journal` folder and run:

```bash
python streamlit_app.py
```
