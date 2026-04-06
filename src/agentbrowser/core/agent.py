"""
LLM factory for agentbrowser.

browser-use >= 0.11 ships its OWN LLM implementations in browser_use.llm.*
that are completely separate from LangChain. These native classes:
  - Are plain dataclasses (no Pydantic), so setattr works freely
  - Have `provider` as a proper property
  - Have `ainvoke(messages, output_format)` with the correct signature
  - Handle structured-output parsing internally

Do NOT use langchain_groq.ChatGroq or langchain_google_genai.ChatGoogleGenerativeAI
with browser-use >= 0.11 — they are incompatible.
"""

from browser_use import Agent
from browser_use.llm.groq.chat import ChatGroq, ToolCallingModels
from browser_use.llm.google.chat import ChatGoogle
from browser_use.llm.exceptions import ModelProviderError
import asyncio
import re
import logging

from agentbrowser.config.settings import Settings

logger = logging.getLogger(__name__)

class RateLimitWrapper:
    """Wraps Gemini LLM to cleanly handle 429 Free Tier Minute Limits."""
    def __init__(self, llm):
        self._llm = llm

    def __getattr__(self, name):
        return getattr(self._llm, name)

    @property
    def provider(self):
        return self._llm.provider

    @property
    def model(self):
        return self._llm.model

    async def ainvoke(self, *args, **kwargs):
        while True:
            try:
                return await self._llm.ainvoke(*args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "resource_exhausted" in error_msg or "too many requests" in error_msg:
                    # Look for "Please retry in XXs." in the error message
                    match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_msg)
                    delay = float(match.group(1)) + 1.0 if match else 30.0
                    
                    logger.warning(f"⚠️ Gemini Rate Limit Hit (15 RPM). Pausing agent for {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue # Retry after sleeping
                raise # Re-raise if not a rate limit error

def build_llm(settings: Settings, llm_provider: str | None = None):
    provider = "gemini" # FORCE Gemini, overriding settings momentarily for stability

    if provider == "groq":

        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in .env")
        
        # Monkey patch: Force browser-use to use Tool Calling instead of JSON Schema
        # for our Llama 3 model, because Groq throws a 400 error for json_schema.
        if settings.groq_model not in ToolCallingModels:
            ToolCallingModels.append(settings.groq_model)

        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0.0,
        )

    if provider == "gemini":
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not set in .env  "
                "(rename GEMINI_API_KEY → GOOGLE_API_KEY in your .env file)"
            )
        llm = ChatGoogle(
            model=settings.gemini_model,
            api_key=settings.google_api_key,
            temperature=0.0,
        )
        return RateLimitWrapper(llm)

    raise ValueError(f"Unknown LLM provider: {provider!r}. Choose 'groq' or 'gemini'.")


def build_agent(
    task: str,
    settings: Settings,
    llm_provider: str | None = None,
    vision: bool = False,
) -> Agent:
    llm = build_llm(settings, llm_provider)
    return Agent(
        task=task,
        llm=llm,
        use_vision=vision,
    )
