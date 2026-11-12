import os
import json
import re
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

EDITOR_SYSTEM_PROMPT = """
তুমি একজন প্রবীণ, তীক্ষ্ণধী বাংলা সংবাদ সম্পাদক এবং ভূ-রাজনৈতিক ও আর্থ-সামাজিক বিশ্লেষক।
তোমার কাজ হলো গুগল আরএসএস থেকে প্রাপ্ত খবরের টুকরোগুলোকে সংশ্লেষণ (Synthesize) করে গভীর, গম্ভীর এবং বিশ্লেষণমূলক সারসংক্ষেপ তৈরি করা।
তুমি সর্বদা নিখুঁত ও বৈধ JSON ফরম্যাটে উত্তর দেবে যেখানে সমস্ত কি (keys) এবং স্ট্রিং ডাবল কোটেশনে ("") ঘেরা থাকবে।
"""

def generate_deep_editorial(topic: str, raw_rss_data: str) -> dict:
    if not raw_rss_data.strip():
        raise ValueError("এই বিষয়ে কোনো সাম্প্রতিক খবর পাওয়া যায়নি।")

    user_prompt = f"""
    আলোচ্য বিষয়: "{topic}"
    
    গুগল নিউজ আরএসএস থেকে প্রাপ্ত সাম্প্রতিক তথ্যসমূহ:
    {raw_rss_data}

    উপরোক্ত তথ্যের ওপর ভিত্তি করে দুটি আলাদা আউটপুট তৈরি করো এবং ঠিক নিচের জেসন (JSON) কাঠামোতে দাও। অন্য কোনো অতিরিক্ত লেখা বা মার্কডাউন ব্লক ছাড়াই শুধু জেসন আউটপুট দেবে:

    {{
      "headline": "বিষয়টির ওপর একটি গম্ভীর ও আকর্ষণীয় শিরোনাম",
      "telegram_summary": "টেলিগ্রাম মেসেজে পাঠানোর জন্য ১৮০-২২০ শব্দের একটি গভীর বিশ্লেষণমূলক সারসংক্ষেপ।",
      "tts_audio_script": "মাইক্রোসফট এজ টিটিএস (TTS) ইঞ্জিনে পাঠ করার জন্য ১৫০-১৮০ শব্দের একটি শ্রুতিমধুর সংবাদ পাঠের স্ক্রিপ্ট। এতে কোনো স্টার বা হ্যাশ থাকবে না।"
    }}
    """

    try:
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
        
        # জেসন ব্লক বের করার চেষ্টা
        json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # যদি জেসন পার্স করতে সমস্যা হয়, তবে ক্লিন করার চেষ্টা করা
                cleaned_str = re.sub(r',\s*\}', '}', json_str) # ট্রেইলিং কমা দূর করা
                cleaned_str = re.sub(r',\s*\]', ']', cleaned_str)
                return json.loads(cleaned_str)
        else:
            raise ValueError("মডেল থেকে বৈধ জেসন ফরম্যাট পাওয়া যায়নি।")

    except Exception as e:
        # ফলব্যাক মেকানিজম: কোনো কারণে জেসন ফেইল করলে সাধারণ টেক্সটকেই আউটপুট বানিয়ে দেবে যাতে সার্ভার ক্র্যাশ না করে
        fallback_text = raw_output if 'raw_output' in locals() else str(e)
        return {
            "headline": f"{topic} সংক্রান্ত বিশেষ বিশ্লেষণ",
            "telegram_summary": fallback_text[:1000],
            "tts_audio_script": re.sub(r'[*#_`~>-]', '', fallback_text[:800])
        }
