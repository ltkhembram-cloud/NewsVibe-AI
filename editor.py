import os
import json
import re
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

EDITOR_SYSTEM_PROMPT = """
তুমি একজন প্রবীণ, তীক্ষ্ণধী বাংলা সংবাদ সম্পাদক এবং ভূ-রাজনৈতিক ও আর্থ-সামাজিক বিশ্লেষক।
তোমার কাজ হলো গুগল আরএসএস থেকে প্রাপ্ত খবরের টুকরোগুলোকে সংশ্লেষণ (Synthesize) করে গভীর, গম্ভীর এবং বিশ্লেষণমূলক সারসংক্ষেপ তৈরি করা।
তুমি সর্বদা নিখুঁত JSON ফরম্যাটে উত্তর দেবে।
"""

def generate_deep_editorial(topic: str, raw_rss_data: str) -> dict:
    if not raw_rss_data.strip():
        raise ValueError("এই বিষয়ে কোনো সাম্প্রতিক খবর পাওয়া যায়নি।")

    user_prompt = f"""
    আলোচ্য বিষয়: "{topic}"
    
    গুগল নিউজ আরএসএস থেকে প্রাপ্ত সাম্প্রতিক তথ্যসমূহ:
    {raw_rss_data}

    উপরোক্ত তথ্যের ওপর ভিত্তি করে দুটি আলাদা আউটপুট তৈরি করো এবং নিচের JSON কাঠামোতে দাও (ভেতরে ডাবল কোটেশন " ব্যবহার করবে না, সিঙ্গেল কোটেশন ' ব্যবহার করবে):

    {{
      "headline": "বিষয়টির ওপর একটি গম্ভীর ও আকর্ষণীয় শিরোনাম",
      "telegram_summary": "টেলিগ্রাম মেসেজে পাঠানোর জন্য ১৮০-২২০ শব্দের একটি গভীর বিশ্লেষণমূলক সারসংক্ষেপ। এতে ঘটনার মূল সত্য, এর পেছনের কারণ এবং ভবিষ্যৎ প্রভাবের তীক্ষ্ণ বিশ্লেষণ থাকবে।",
      "tts_audio_script": "মাইক্রোসফট এজ টিটিএস (TTS) ইঞ্জিনে পাঠ করার জন্য ১৫০-১৮০ শব্দের একটি শ্রুতিমধুর, গম্ভীর সংবাদ পাঠের স্ক্রিপ্ট। এতে কোনো স্টার (*), হ্যাশ (#), বুলেট পয়েন্ট বা ব্র্যাকেট থাকবে না—সম্পূর্ণ প্রমিত ও ছন্দময় অনুচ্ছেদে লেখা থাকবে।"
    }}
    """

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": EDITOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.35,
        max_completion_tokens=4096
    )

    raw_output = completion.choices[0].message.content.strip()
    json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    
    if json_match:
        return json.loads(json_match.group(0))
    else:
        # যদি কোনো কারণে JSON মিস হয়, ফলব্যাক হিসেবে সরাসরি টেক্সট রিটার্ন করবে
        return {
            "headline": f"{topic} সংক্রান্ত বিশেষ বিশ্লেষণ",
            "telegram_summary": raw_output,
            "tts_audio_script": re.sub(r'[*#_`~>-]', '', raw_output)
        }
  
