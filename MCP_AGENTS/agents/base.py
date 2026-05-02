"""
RecruitSight - Base Agent Runner
Reusable async agent executor with retry logic, structured output parsing,
and failure handling via the Google GenAI SDK.
"""

import asyncio
import json
import logging
import re
import traceback
from typing import Type, TypeVar

import json_repair
from pydantic import BaseModel

from config import (
    client,
    MODEL_FLASH,
    MODEL_GEMINI_FALLBACK,
    MAX_RETRIES,
    BASE_BACKOFF_SECONDS,
    DEFAULT_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
)
import google.generativeai as genai

logger = logging.getLogger("recruitsight.agent")

T = TypeVar("T", bound=BaseModel)

async def _run_gemini_agent(
    agent_name: str,
    augmented_system_prompt: str,
    user_content: str,
    response_schema: Type[T],
    model_name: str = MODEL_GEMINI_FALLBACK,
    temperature: float = DEFAULT_TEMPERATURE,
) -> T | None:
    """Helper to run the Gemini agent natively using google-genai."""
    logger.info(f"[{agent_name}] Running native Gemini fallback via {model_name}...")
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=augmented_system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json",
            )
        )

        # google.generativeai synchronous call via thread to avoid blocking event loop
        response = await asyncio.to_thread(
            model.generate_content,
            user_content
        )

        content = response.text.strip()

        # Strip markdown code fences if model added them
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Attempt 1: lenient parse (accepts embedded control chars like \n/\t)
        try:
            data = json.loads(content, strict=False)
        except json.JSONDecodeError as e1:
            logger.warning(
                f"[{agent_name}] Gemini lenient JSON parse failed ({e1}). "
                "Attempting json-repair..."
            )
            try:
                # json-repair handles missing quotes, unescaped chars, and bad delimiters
                data = json_repair.loads(content)
            except Exception as e2:
                logger.warning(f"[{agent_name}] json-repair also failed: {e2}. Final fallback: regex sanitization.")
                # Attempt 3: strip bare control characters and retry
                sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)
                data = json.loads(sanitized, strict=False)

        result = response_schema.model_validate(data)
        logger.info(f"[{agent_name}] ✅ Gemini Success")
        return result
    except Exception as e:
        logger.error(f"[{agent_name}] ❌ Gemini Fallback FAILED: {type(e).__name__}: {e}")
        return None

async def run_agent(
    agent_name: str,
    system_prompt: str,
    user_content: str,
    response_schema: Type[T],
    tools: list = None,
    model: str = MODEL_FLASH,
    max_retries: int = MAX_RETRIES,
    temperature: float = DEFAULT_TEMPERATURE,
) -> T | None:
    last_error = None

    # Inject JSON schema into the system prompt to enforce structured output for free models
    schema_str = json.dumps(response_schema.model_json_schema(), indent=2)
    augmented_system_prompt = (
        f"{system_prompt}\n\n"
        f"IMPORTANT: You MUST return your response as a valid JSON object matching the exact schema below.\n"
        f"Do not include any introductory or explanatory text. Return ONLY the JSON object.\n"
        f"SCHEMA:\n{schema_str}"
    )

    # If the requested model IS the Gemini fallback, run it directly and skip OpenRouter.
    if model == MODEL_GEMINI_FALLBACK:
        return await _run_gemini_agent(agent_name, augmented_system_prompt, user_content, response_schema, model, temperature)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"[{agent_name}] Attempt {attempt}/{max_retries} using {model}"
            )

            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": augmented_system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": temperature,
                "max_tokens": MAX_OUTPUT_TOKENS,
            }

            response = await client.chat.completions.create(**kwargs)

            # Check for block reasons
            if not response.choices or not response.choices[0].message.content:
                finish_reason = response.choices[0].finish_reason if response.choices else "UNKNOWN"
                logger.warning(f"[{agent_name}] Empty response on attempt {attempt}. Finish reason: {finish_reason}")
                last_error = f"Model returned empty response (Reason: {finish_reason})"
                continue

            content = response.choices[0].message.content.strip()

            # Clean up markdown code blocks if the model erroneously included them
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            try:
                logger.info(f"[{agent_name}] Parsing JSON text...")
                try:
                    data = json.loads(content, strict=False)
                except json.JSONDecodeError:
                    logger.warning(f"[{agent_name}] JSON parse error, attempting json-repair...")
                    data = json_repair.loads(content)
                
                result = response_schema.model_validate(data)
                logger.info(f"[{agent_name}] ✅ Success")
                return result
            except Exception as e:
                logger.warning(f"[{agent_name}] JSON/Pydantic error: {e}. Snippet: {content[:100]}...")
                last_error = f"Parse error: {e}"
                continue

        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            logger.warning(f"[{agent_name}] {last_error} on attempt {attempt}")
            logger.debug(traceback.format_exc())

        # Exponential backoff before retry
        if attempt < max_retries:
            wait = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.info(f"[{agent_name}] Retrying in {wait}s...")
            await asyncio.sleep(wait)

    logger.error(
        f"[{agent_name}] ❌ FAILED after {max_retries} attempts with OpenRouter. Last error: {last_error}"
    )
    
    # Fallback to Gemini 2.5 Flash
    logger.warning(f"[{agent_name}] Falling back to native {MODEL_GEMINI_FALLBACK}...")
    return await _run_gemini_agent(agent_name, augmented_system_prompt, user_content, response_schema, MODEL_GEMINI_FALLBACK, temperature)
