import edge_tts

async def create_deep_voice_audio(script_text: str, output_path: str = "audio_overview.mp3") -> str:
    """
    Microsoft Edge TTS ব্যবহার করে গাঢ় ও গম্ভীর বাংলা পুরুষ কণ্ঠে অডিও তৈরি করে।
    """
    voice = "bn-IN-BashkarNeural"
    
    communicate = edge_tts.Communicate(
        text=script_text,
        voice=voice,
        pitch="-12Hz",  # গম্ভীর ও ভারী বেস (Deep Bass)
        rate="-6%"     # ধীর ও স্পষ্ট সংবাদ পাঠের গতি
    )
    await communicate.save(output_path)
    return output_path
  
