FROM python:3.11-slim

WORKDIR /app

# সিস্টেম ডিপেন্ডেন্সি ও সার্টিফিকেট আপডেট
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# লাইব্রেরি ইনস্টল
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# সমস্ত প্রজেক্ট ফাইল কপি করা
COPY rss_fetcher.py editor.py tts.py api_server.py ./

# অডিও সেভ করার জন্য ফোল্ডার তৈরি
RUN mkdir -p /tmp/audio_files

# Koyeb-এর জন্য পোর্ট এক্সপোজ করা
EXPOSE 8000

# FastAPI সার্ভার চালু করা
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
