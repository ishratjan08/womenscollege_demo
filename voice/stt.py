import speech_recognition as sr
from pydub import AudioSegment
import os

def speech_to_text(audio_path):
    # Convert any format → wav
    wav_path = audio_path + ".wav"
    AudioSegment.from_file(audio_path).export(wav_path, format="wav")

    r = sr.Recognizer()

    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
        text = r.recognize_google(audio)
        print("input text:: ", text)

    os.remove(wav_path)  # clean

    return text