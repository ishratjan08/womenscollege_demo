from gtts import gTTS
import uuid
import os

def text_to_speech(text):
    # ensure outputs/ folder exists
    os.makedirs("outputs", exist_ok=True)

    filename = f"tts_output_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("outputs", filename)

    tts = gTTS(text)
    tts.save(filepath)

    # return ONLY filename, not full path
    return filename