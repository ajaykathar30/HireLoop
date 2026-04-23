"""
RecruitSight — Base Agent Runner
Reusable async agent executor with retry logic, structured output parsing,
and failure handling via the Google GenAI SDK.
"""

import asyncio
import json
import logging
import traceback
from typing import Type, TypeVar

from pydantic import BaseModel

from google.genai import types
from config import (
    client,
    MODEL_FLASH,
    MAX_RETRIES,
    BASE_BACKOFF_SECONDS,
    DEFAULT_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
)

logger = logging.getLogger("recruitsight.agent")

T = TypeVar("T", bound=BaseModel)


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
    """
    Core agent executor.
    
    1. Calls client.aio.models.generate_content() with response_schema
    2. Supports function calling via the tools parameter
    3. Retries with exponential backoff on failure
    4. Returns parsed Pydantic model via response.parsed
    
    Args:
        agent_name: Human-readable name for logging
        system_prompt: System instruction for the agent
        user_content: The user message / data to analyze
        response_schema: Pydantic model class for structured output
        tools: List of function tools for the model to use
        model: Gemini model ID to use
        max_retries: Maximum retry attempts
        temperature: Generation temperature
    
    Returns:
        Parsed Pydantic model instance, or None on total failure
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"[{agent_name}] Attempt {attempt}/{max_retries} using {model}"
            )

            # Define safety settings to prevent blocking on source code
            safety_settings = [
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_CIVIC_INTEGRITY", threshold="BLOCK_NONE"),
            ]

            # Build config — tools and response_schema cannot always coexist;
            # only add tool-related fields when tools are explicitly requested.
            config_kwargs = dict(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=temperature,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                safety_settings=safety_settings,
            )
            if tools:
                config_kwargs["tools"] = tools
                config_kwargs["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(
                    disable=False
                )

            config = types.GenerateContentConfig(**config_kwargs)

            response = await client.aio.models.generate_content(
                model=model,
                contents=user_content,
                config=config,
            )

            # Check for block reasons
            if not response.candidates or not response.candidates[0].content:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                logger.warning(f"[{agent_name}] Empty response on attempt {attempt}. Finish reason: {finish_reason}")
                last_error = f"Model returned empty response (Reason: {finish_reason})"
                continue

            # Try to use the auto-parsed result first
            if response.parsed is not None:
                logger.info(f"[{agent_name}] ✅ Success (parsed directly)")
                return response.parsed

            # Fallback: manually parse the text response
            if response.text:
                logger.info(f"[{agent_name}] Parsing JSON text fallback...")
                data = json.loads(response.text)
                result = response_schema.model_validate(data)
                logger.info(f"[{agent_name}] ✅ Success (manual parse)")
                return result

            logger.warning(f"[{agent_name}] Empty response on attempt {attempt}")
            last_error = "Empty response from model"

        except json.JSONDecodeError as e:
            last_error = f"JSON parse error: {e}"
            logger.warning(f"[{agent_name}] {last_error} on attempt {attempt}")

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
        f"[{agent_name}] ❌ FAILED after {max_retries} attempts. Last error: {last_error}"
    )
    return None
