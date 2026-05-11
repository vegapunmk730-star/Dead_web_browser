import os
import anthropic
from config.settings import settings
from infrastructure.logging.logger import get_logger

log = get_logger("ai.repair")

# Lazy client — initialized on first call, not at import time
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client

SYSTEM = """You are a digital archaeologist and web reconstruction engine.

Your mission: repair broken HTML recovered from the Internet Archive.

STRICT RULES:
1. PRESERVE all original content and text — never hallucinate or invent facts
2. FIX broken HTML structure: unclosed tags, malformed nesting, missing elements
3. REMOVE dead external references that cause console errors
4. REBUILD obvious missing CSS inline where structure clearly requires it
5. MARK AI-generated sections: <!-- [DWN:reconstructed] -->
6. DO NOT redesign or change visual intent
7. RETURN ONLY valid HTML — no explanations, no markdown fences

You are reconstructing history. Accuracy and fidelity are everything."""


def ai_repair(html: str, original_url: str) -> str:
    trimmed = html[:settings.ai_html_trim]
    prompt = f"""Repair this archived HTML recovered from: {original_url}

HTML:
{trimmed}"""

    try:
        client = _get_client()
        msg = client.messages.create(
            model=settings.ai_model,
            max_tokens=settings.ai_max_tokens,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.content[0].text.strip()
        if len(result) > 200 and "<" in result:
            log.info("AI repair successful", url=original_url)
            return result
    except Exception as e:
        log.error("AI repair failed", error=str(e), url=original_url)

    return html
