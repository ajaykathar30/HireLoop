import httpx
import logging
from core.config import settings
from typing import Optional, AsyncGenerator
import base64

logger = logging.getLogger(__name__)

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

# ---------------------------------------------------------------------------
# TEXT TO SPEECH  — Sarvam AI Bulbul v3 (REST, synchronous)
#
# Docs: https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/text-to-speech/rest-api
#
# Request  POST /text-to-speech
# Body:
#   text                 string  — the text to synthesise
#   target_language_code string  — e.g. "en-IN"
#   speaker              string  — e.g. "meera" / "shubh"
#   model                string  — "bulbul:v3"
#
# Response:
#   { "request_id": "...", "audios": ["<base64-WAV-string>"] }
#   Default codec: WAV (24 kHz). Decoded bytes are playable .wav audio.
# ---------------------------------------------------------------------------

async def text_to_speech(
    text: str,
    language_code: str = "en-IN",
    speaker: str = "priya",
) -> Optional[bytes]:
    """
    Converts text to speech using Sarvam AI REST API.
    Returns raw WAV bytes or None on failure.
    """
    if not settings.SARVAM_API_KEY:
        logger.error("SARVAM_API_KEY is not set")
        return None

    headers = {
        "api-subscription-key": settings.SARVAM_API_KEY,
        "Content-Type": "application/json",
    }
    # IMPORTANT: REST API uses singular "text" key (NOT "inputs" array)
    payload = {
        "text": text,
        "target_language_code": language_code,
        "speaker": speaker,
        "model": "bulbul:v3",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SARVAM_TTS_URL, headers=headers, json=payload, timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                audios = data.get("audios", [])
                if audios:
                    # Sarvam returns base64-encoded WAV — decode to raw bytes
                    return base64.b64decode(audios[0])
                else:
                    logger.error(f"Sarvam TTS returned no audios: {data}")
            else:
                logger.error(
                    f"Sarvam TTS HTTP {response.status_code}: {response.text}"
                )
        except httpx.TimeoutException:
            logger.error("Sarvam TTS request timed out")
        except Exception as e:
            logger.error(f"Sarvam TTS exception: {e}")

    return None


async def stream_text_to_speech(
    text: str,
    language_code: str = "en-IN",
    speaker: str = "priya",
) -> AsyncGenerator[bytes, None]:
    """
    Yields WAV audio bytes for the given text via Sarvam REST API.
    Uses the simple REST API (not WebSocket) — sufficient for short
    interview questions and much more reliable in production.
    """
    audio_bytes = await text_to_speech(text, language_code, speaker)
    if audio_bytes:
        yield audio_bytes
    else:
        logger.warning("stream_text_to_speech: TTS returned no audio; yielding silence")


# ---------------------------------------------------------------------------
# SPEECH TO TEXT — Groq Whisper
#
# Docs: https://console.groq.com/docs/api-reference#audio-transcription
#
# Endpoint: POST https://api.groq.com/openai/v1/audio/transcriptions
# Required multipart fields:
#   file    — audio file object (webm / wav / mp3 / etc.)
#   model   — "whisper-large-v3-turbo"
# Optional:
#   language        — ISO-639-1 code ("en") for accuracy + latency
#   response_format — "json" (default) → { "text": "..." }
# ---------------------------------------------------------------------------

async def speech_to_text(
    audio_content: bytes,
    language_code: str = "en-IN",
) -> Optional[str]:
    """
    Transcribes audio bytes using Groq Whisper (whisper-large-v3-turbo).
    Accepts webm (browser MediaRecorder default), wav, mp3, and more.
    Returns the transcript string or None on failure.
    """
    if not settings.GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not set")
        return None

    # Guard: less than 100 bytes is not real audio (empty/corrupt blob)
    if not audio_content or len(audio_content) < 100:
        logger.warning(
            f"Skipping STT — audio too small ({len(audio_content) if audio_content else 0} bytes)"
        )
        return None

    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    # Browser MediaRecorder records as audio/webm;codecs=opus — Groq accepts it
    files = {"file": ("audio.webm", audio_content, "audio/webm")}
    data = {
        "model": "whisper-large-v3-turbo",
        # ISO-639-1: strip country suffix  ("en-IN" → "en")
        "language": language_code.split("-")[0],
        "response_format": "json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                GROQ_STT_URL, headers=headers, data=data, files=files, timeout=30.0
            )
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("text", "").strip()
                logger.info(
                    f"Groq STT: {len(transcript)} chars — '{transcript[:80]}'"
                )
                return transcript or None
            else:
                logger.error(
                    f"Groq STT HTTP {response.status_code}: {response.text}"
                )
        except httpx.TimeoutException:
            logger.error("Groq STT request timed out after 30s")
        except Exception as e:
            logger.error(f"Groq STT exception: {e}")

    return None
