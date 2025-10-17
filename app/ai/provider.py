# app/ai/provider.py
import os

PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

if PROVIDER == "openrouter":
    from .service_openrouter import ask_openrouter as ask_ai
elif PROVIDER == "ollama":
    from .service_ollama import ask_ollama as ask_ai
else:
    from .service_gemini import ask_gemini as ask_ai
