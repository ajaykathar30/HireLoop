import httpx
import logging
from core.config import settings
from typing import Optional, AsyncGenerator
import websockets
import json
import base64

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
    Converts speech to text using Groq Whisper (whisper-large-v3-turbo) for ultra-low latency.
    Expects raw audio bytes (wav).
    """
    if not settings.GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set")
        return None

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}"
    }
    
    # Prepare multipart form data
    files = {
        "file": ("audio.webm", audio_content, "audio/webm")
    }
    data = {
        "model": "whisper-large-v3-turbo",
        # Groq expects 'en', 'es', etc.
        "language": language_code.split("-")[0],
        "response_format": "json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=data, files=files, timeout=10.0)
            if response.status_code == 200:
                result = response.json()
                return result.get("text")
            else:
                logger.error(f"Groq STT Error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Groq STT Exception: {e}")
            
    return None

async def stream_text_to_speech(text: str, language_code: str = "en-IN", speaker: str = "shubh") -> AsyncGenerator[bytes, None]:
    """
    Streams text to speech using Sarvam AI via WebSocket.
    Yields audio chunks (bytes) as they are synthesized.
    """
    if not settings.SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY not set")
        return

    # Use the streaming endpoint
    url = "wss://api.sarvam.ai/text-to-speech"
    
    # Pass auth header
    headers = {
        "api-subscription-key": settings.SARVAM_API_KEY
    }
    
    payload = {
        "text": text,
        "target_language_code": language_code,
        "speaker": speaker,
        "model": "bulbul:v3"
    }

    try:
        async with websockets.connect(url, extra_headers=headers) as ws:
            await ws.send(json.dumps(payload))
            async for message in ws:
                if isinstance(message, str):
                    try:
                        data = json.loads(message)
                        if "audio" in data:
                            yield base64.b64decode(data["audio"])
                        elif "error" in data:
                            logger.error(f"Sarvam Streaming TTS Error: {data['error']}")
                    except json.JSONDecodeError:
                        pass
                else:
                    # If the websocket returns raw binary chunks
                    yield message
    except Exception as e:
        logger.error(f"Sarvam Streaming TTS Exception: {e}")

