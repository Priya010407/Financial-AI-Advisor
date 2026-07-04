import speech_recognition as sr
import tempfile
import os


def transcribe_audio_file(audio_file):

    recognizer = sr.Recognizer()

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name

        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)

        os.remove(tmp_path)

        return {
            "status": "success",
            "text": text
        }

    except sr.UnknownValueError:
        return {
            "status": "error",
            "text": "Could not understand audio"
        }

    except Exception as e:
        return {
            "status": "error",
            "text": str(e)
        }


def parse_voice_expense(text):

    text = text.lower()

    amount = 0
    category = "Other"

    words = text.split()

    for w in words:
        if w.replace(".", "").isdigit():
            amount = float(w)

    if any(x in text for x in ["food", "restaurant", "burger", "pizza"]):
        category = "Food & Dining"

    elif any(x in text for x in ["shop", "clothes", "amazon"]):
        category = "Shopping"

    elif any(x in text for x in ["bus", "uber", "train"]):
        category = "Transportation"

    elif any(x in text for x in ["doctor", "hospital", "medicine"]):
        category = "Medical"

    return {
        "amount": amount,
        "category": category,
        "raw_text": text
    }