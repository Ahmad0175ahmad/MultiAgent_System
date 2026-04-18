"""
LLM Router Module (M2)

Routes requests between:
- Groq (fast cloud)
- Gemini (long context)

Author: AutoAgent
"""

from typing import Optional
import logging
import time

from config import settings

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from google import genai
except ImportError:
    genai = None


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LLMRouter:
    """
    Routes LLM requests across supported API providers.
    """

    _shared_provider_backoff_until: dict[str, float] = {}

    def __init__(self, preferred_provider: Optional[str] = None, preferred_model: Optional[str] = None):
        self.preferred_provider = (preferred_provider or settings.DEFAULT_LLM_PROVIDER or "").lower()
        self.default_model = preferred_model or settings.DEFAULT_LLM_MODEL
        self.groq_model = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        self.gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")

        self.groq_client = None
        if getattr(settings, "GROQ_API_KEY", None) and Groq:
            try:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.error("Groq init failed: %s", e)

        self.gemini_client = None
        if getattr(settings, "GEMINI_API_KEY", None) and genai:
            try:
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error("Gemini init failed: %s", e)

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        token_count: Optional[int] = None,
        speed_priority: bool = False,
        provider: Optional[str] = None,
        timeout: Optional[float] = None,
        num_predict: Optional[int] = None,
        response_format: Optional[str] = None,
    ) -> str:
        """
        Main routing method.
        """
        _ = task_type
        _ = num_predict
        _ = response_format

        requested_provider = (provider or self.preferred_provider or settings.DEFAULT_LLM_PROVIDER or "").lower()

        try:
            if self._is_provider_in_backoff(requested_provider):
                logger.warning(
                    "Provider %s is in temporary backoff, using fallback routing",
                    requested_provider,
                )
                requested_provider = ""

            if requested_provider == "groq" and self.groq_client:
                logger.info("Routing to Groq (requested)")
                return self._groq_chat(prompt, system_prompt, timeout=timeout)

            if requested_provider == "gemini" and self.gemini_client and settings.GEMINI_API_KEY:
                logger.info("Routing to Gemini (requested)")
                return self._gemini_chat(prompt, system_prompt, timeout=timeout)

            if token_count and token_count > 4000 and self.gemini_client and settings.GEMINI_API_KEY:
                logger.info("Routing to Gemini (long context)")
                return self._gemini_chat(prompt, system_prompt, timeout=timeout)

            if speed_priority and self.groq_client:
                logger.info("Routing to Groq (speed priority)")
                return self._groq_chat(prompt, system_prompt, timeout=timeout)

            if self.groq_client:
                logger.info("Routing to Groq (default)")
                return self._groq_chat(prompt, system_prompt, timeout=timeout)

            if self.gemini_client and settings.GEMINI_API_KEY:
                logger.info("Routing to Gemini (default fallback)")
                return self._gemini_chat(prompt, system_prompt, timeout=timeout)

            raise RuntimeError("No configured LLM provider is available.")

        except Exception as e:
            logger.error("Primary routing failed: %s", e)
            self._mark_provider_failure(requested_provider, e)

            if requested_provider != "groq" and self.groq_client:
                try:
                    logger.info("Falling back to Groq")
                    return self._groq_chat(prompt, system_prompt, timeout=timeout)
                except Exception as fallback_error:
                    logger.error("Groq fallback failed: %s", fallback_error)

            if requested_provider != "gemini" and self.gemini_client and settings.GEMINI_API_KEY:
                try:
                    logger.info("Falling back to Gemini")
                    return self._gemini_chat(prompt, system_prompt, timeout=timeout)
                except Exception as gemini_error:
                    logger.error("Gemini fallback failed: %s", gemini_error)

            raise RuntimeError("All LLM providers failed.")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        token_count: Optional[int] = None,
        speed_priority: bool = False,
        max_tokens: Optional[int] = None,
        provider: Optional[str] = None,
        timeout: Optional[float] = None,
        num_predict: Optional[int] = None,
        response_format: Optional[str] = None,
    ) -> str:
        """
        Backward-compatible alias used by agents.
        """
        _ = max_tokens
        return self.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type=task_type,
            token_count=token_count,
            speed_priority=speed_priority,
            provider=provider,
            timeout=timeout,
            num_predict=num_predict or max_tokens,
            response_format=response_format,
        )

    def _mark_provider_failure(self, provider: str, error: Exception) -> None:
        """Temporarily back off flaky providers after network-like failures."""
        if not provider:
            return

        error_text = str(error).lower()
        if "timed out" in error_text or "connection" in error_text:
            self._shared_provider_backoff_until[provider] = time.time() + 120

    def _is_provider_in_backoff(self, provider: str) -> bool:
        if not provider:
            return False

        until = self._shared_provider_backoff_until.get(provider)
        if until is None:
            return False
        if time.time() >= until:
            self._shared_provider_backoff_until.pop(provider, None)
            return False
        return True

    def _resolve_timeout(self, requested_timeout: Optional[float]) -> float:
        return float(requested_timeout) if requested_timeout is not None else 45.0

    def _groq_chat(
        self,
        prompt: str,
        system_prompt: Optional[str],
        timeout: Optional[float] = None,
    ) -> str:
        """Call Groq API."""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            completion = self.groq_client.chat.completions.create(
                model=self.groq_model if self.preferred_provider != "groq" else self.default_model,
                messages=messages,
                timeout=self._resolve_timeout(timeout),
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error("Groq error: %s", e)
            raise

    def _gemini_chat(
        self,
        prompt: str,
        system_prompt: Optional[str],
        timeout: Optional[float] = None,
    ) -> str:
        """Call Gemini API."""
        _ = timeout
        try:
            model_name = self.gemini_model if self.preferred_provider != "gemini" else self.default_model
            full_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"

            response = self.gemini_client.models.generate_content(
                model=model_name,
                contents=full_prompt,
            )
            return (response.text or "").strip()

        except Exception as e:
            logger.error("Gemini error: %s", e)
            raise


if __name__ == "__main__":
    router = LLMRouter()
    print(router.chat("Say hello in one word"))
