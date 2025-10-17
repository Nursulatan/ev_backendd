# app/assistant/tts_openai.py
import os
import requests
from openai import OpenAI
from io import BytesIO

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def text_to_speech_openai(text: str, voice: str = "alloy") -> bytes:
    """
    OpenAI TTS (text-to-speech)
    """
    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",  # OpenAI үн модели
            voice=voice,
            input=text,
        )
        # Натыйжаны MP3 форматта алабыз
        audio_data = response.read()
        return audio_data
    except Exception as e:
        return f"TTS error: {e}".encode()
