import os
import uuid
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rss_fetcher import fetch_google_rss_news
from editor import generate_deep_editorial
from tts import create_deep_voice_audio

app = FastAPI(
    title="Bengali Deep News & Audio Overview API",
    description="Google RSS + Groq (gpt-oss-20b) + Deep Male Edge-TTS Pipeline",
    version="1.0.0"
)

AUDIO_DIR = "/tmp/audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

class NewsRequest(BaseModel):
    query: str
    max_items: int = 5

@app.get("/")
def health_check():
    return {"status": "online", "message": "গুরুদেবের নিউজ ও অডিও এপিআই সার্ভার সচল আছে!"}

@app.post("/generate-news")
async def generate_news_endpoint(req: NewsRequest):
    try:
        # ধাপ ১: গুগল আরএসএস থেকে খবর সংগ্রহ
        raw_rss = fetch_google_rss_news(req.query, req.max_items)
        if not raw_rss:
            raise HTTPException(status_code=404, detail="এই বিষয়ে কোনো খবর পাওয়া যায়নি।")

        # ধাপ ২: editor.py দিয়ে বিশ্লেষণমূলক সামারি ও অডিও স্ক্রিপ্ট তৈরি
        editorial = generate_deep_editorial(req.query, raw_rss)

        # ধাপ ৩: tts.py দিয়ে গম্ভীর কণ্ঠে অডিও তৈরি
        file_id = f"news_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(AUDIO_DIR, file_id)
        await create_deep_voice_audio(editorial["tts_audio_script"], audio_path)

        # টেলিগ্রাম বটে সহজে পাঠানোর জন্য অডিওটিকে Base64 এবং ডাউনলোড পাথ দুভাবেই দেওয়া হলো
        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")

        return {
            "status": "success",
            "query": req.query,
            "headline": editorial["headline"],
            "summary": editorial["telegram_summary"],
            "audio_script": editorial["tts_audio_script"],
            "audio_filename": file_id,
            "audio_download_endpoint": f"/download-audio/{file_id}",
            "audio_base64": audio_base64
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-audio/{filename}")
def download_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="অডিও ফাইলটি পাওয়া যায়নি।")
    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
  
