import httpx
import logging
from core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

SARVAM_BASE_URL = "https://api.sarvam.ai"

async def text_to_speech(text: str, language_code: str = "en-IN", speaker: str = "shubh") -> Optional[str]:
    """
    Converts text to speech using Sarvam AI Bulbul v3.
    Returns base64 encoded audio string.
    """
    if not settings.SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY not set")
        return None

    url = f"{SARVAM_BASE_URL}/text-to-speech"
    headers = {
        "api-subscription-key": settings.SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "target_language_code": language_code,
        "speaker": speaker,
        "model": "bulbul:v3"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                # Sarvam returns an array of audios
                if "audios" in data and len(data["audios"]) > 0:
                    return data["audios"][0]
            else:
                logger.error(f"Sarvam TTS Error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Sarvam TTS Exception: {e}")
    
    return None

async def speech_to_text(audio_content: bytes, language_code: str = "en-IN") -> Optional[str]:
    """
    Converts speech to text using Sarvam AI Saaras v3.
    Expects raw audio bytes (wav).
    """
    if not settings.SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY not set")
        return None

    url = f"{SARVAM_BASE_URL}/speech-to-text"
    headers = {
        "api-subscription-key": settings.SARVAM_API_KEY
    }
    
    # Prepare multipart form data
    files = {
        "file": ("audio.wav", audio_content, "audio/wav")
    }
    data = {
        "model": "saaras:v3",
        "mode": "transcribe",
        "language_code": language_code
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=data, files=files, timeout=30.0)
            if response.status_code == 200:
                result = response.json()
                return result.get("transcript")
            else:
                logger.error(f"Sarvam STT Error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Sarvam STT Exception: {e}")
            
    return None
