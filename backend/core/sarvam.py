import httpx
import logging
from core.config import settings
from typing import Optional, AsyncGenerator
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
    Converts speech to text using Sarvam AI STT.
    Expects raw audio bytes.
    """
    if not settings.SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY not set")
        return None

    from sarvamai import AsyncSarvamAI
    client = AsyncSarvamAI(api_subscription_key=settings.SARVAM_API_KEY)

    try:
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_content)
            tmp_path = tmp.name

        try:
            response = await client.speech_to_text.transcribe(
                file=open(tmp_path, "rb"),  # ✅ Open as binary file object
                model="saaras:v3",          # ✅ Use recommended model
                language_code=language_code
            )
            return response.transcript      # ✅ Attribute access, not .get()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        logger.error(f"Sarvam STT Exception: {e}")

    return None


from sarvamai import AsyncSarvamAI, AudioOutput, EventResponse

async def stream_text_to_speech(text: str, language_code: str = "en-IN", speaker: str = "shubh") -> AsyncGenerator[bytes, None]:
    """
    Streams text to speech using the official Sarvam AI SDK.
    """
    if not settings.SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY not set")
        return

    client = AsyncSarvamAI(api_subscription_key=settings.SARVAM_API_KEY)

    try:
        async with client.text_to_speech_streaming.connect(
            model="bulbul:v3", 
            send_completion_event=True
        ) as ws:
            # 1. Configure
            await ws.configure(
                target_language_code=language_code,
                speaker=speaker,
                output_audio_codec="wav"
            )
            
            # 2. Convert text
            await ws.convert(text)
            
            # 3. Flush buffer
            await ws.flush()

            # 4. Stream audio chunks
            async for message in ws:
                if isinstance(message, AudioOutput):
                    # The SDK already handles base64 decoding for us in most versions, 
                    # but if it returns a string in message.data.audio, we decode.
                    # Based on docs, it might be base64.
                    yield base64.b64decode(message.data.audio)
                elif isinstance(message, EventResponse):
                    if message.data.event_type == "final":
                        break
    except Exception as e:
        logger.error(f"Sarvam SDK Streaming TTS Exception: {e}")

