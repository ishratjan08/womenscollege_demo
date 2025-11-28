from fastapi import APIRouter, Query, UploadFile, File
from services.query_service import chat_engine
from voice.stt import speech_to_text
from voice.tts import text_to_speech
import uuid
import os
router = APIRouter()

# Text based chat
@router.post("/chat")
async def chat_with_your_rag(user_query: str = Query(...),
                             session_id: str = Query(...),
                             user_id: str = Query(...)):
    response = chat_engine.run_chat(user_query, session_id, user_id)
    return {"Message": response}

@router.post("/chat/audio")
async def chat_with_audio(
    audio: UploadFile = File(...),
    session_id: str = Query(...),
    user_id: str = Query(...)
):
    # Save incoming audio
    temp_audio_path = f"input_audio/{uuid.uuid4()}.wav"
    with open(temp_audio_path, "wb") as f:
        f.write(await audio.read())

    # 1️⃣ Convert Speech to Text
    text_query = speech_to_text(temp_audio_path)

    # 2️⃣ Chat Response
    response_text = chat_engine.run_chat(text_query, session_id, user_id)

    # 3️⃣ Convert Text → Audio (TTS)
    output_audio_path = text_to_speech(response_text)
    # Example: returns something like "tts_output/abcd1234.mp3"

    # 4️⃣ Return JSON + Downloadable Audio URL
    return {
        "text": text_query,
        "message": response_text,
        "audio_url": f"/response_audio/{os.path.basename(output_audio_path)}"
    }
