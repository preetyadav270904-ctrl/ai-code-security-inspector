import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

if not GROQ_API_KEY.startswith("gsk_"):
    if os.getenv("CI_TEST_MODE") != "1":
        print("[!] Warning: GROQ_API_KEY not configured or invalid in .env")