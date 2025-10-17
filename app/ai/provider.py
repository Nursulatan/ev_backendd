from app.assistant.commands import handle_local_command
from app.ai.service_gemini import ask_gemini
import os

AI_PROVIDER = os.getenv("AI_PROVIDER","gemini").lower()

def answer_text(message: str) -> str | dict:
    local = handle_local_command(message)
    if local:
        # Машинага жөнөтүү үчүн dict кайтарып жатсаң — ошол боюнча колдонуңуз.
        # UIга адамча текст көрсөтсөңүз, local.get("say") колдонсоңуз болот.
        return local
    if AI_PROVIDER == "gemini":
        return {"type":"chat","answer": ask_gemini(message)}
    return {"type":"chat","answer":"Команда түшүнүксүз 🙏"}
