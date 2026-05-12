import asyncio
import os
from typing import Any, Dict, Optional

from openai import AsyncOpenAI

_SECTION_LABELS = {
    "model": "C# ViewModel class",
    "controller": "C# MVC Controller",
    "main_view": "Razor main/index view (.cshtml)",
    "list_view": "Razor list partial view (.cshtml)",
    "document_view": "Razor document detail view (.cshtml)",
}


class AICodeEnhancer:
    """Enhances generated MVC code sections in parallel using OpenAI."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL")

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def enhance_full_code(
        self,
        generated_code: Dict[str, Optional[str]],
        page_name: str,
        entity_name: str,
        parser_summary: Dict[str, Any],
        user_prompt: Optional[str],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """
        Refine all MVC code sections in parallel.
        Each section is a separate async OpenAI call so they run concurrently —
        total latency ≈ slowest single section instead of the sum of all sections.
        """
        if not self.is_available():
            raise ValueError("OPENAI_API_KEY is not configured on the server")

        instruction = (
            user_prompt.strip()
            if user_prompt and user_prompt.strip()
            else "Improve maintainability, naming clarity, null safety, and validation without changing behavior."
        )

        resolved_model = model or self.default_model

        client_kwargs: Dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = AsyncOpenAI(**client_kwargs)

        async def _enhance_section(section_key: str, section_code: str) -> tuple[str, str]:
            """Refine one code section. Returns (key, refined_code)."""
            label = _SECTION_LABELS.get(section_key, section_key)
            system_msg = (
                f"You are an expert C# ASP.NET MVC code assistant. "
                f"You will receive one {label} file. "
                f"Apply the instruction below, then return ONLY the improved code — "
                f"no explanation, no markdown fences, no JSON wrapper. "
                f"Preserve all existing endpoint names, method signatures, and architecture. "
                f"Do not remove any existing functionality.\n\n"
                f"Instruction: {instruction}"
            )
            user_msg = (
                f"Page name: {page_name}\n"
                f"Entity name: {entity_name}\n\n"
                f"{section_code}"
            )
            response = await client.chat.completions.create(
                model=resolved_model,
                temperature=temperature,
                max_tokens=max_output_tokens,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )
            refined = response.choices[0].message.content
            return section_key, (refined.strip() if refined else section_code)

        code_keys = ["model", "controller", "main_view", "list_view", "document_view"]

        # Only create tasks for sections that actually have content
        tasks = [
            _enhance_section(key, generated_code[key])
            for key in code_keys
            if generated_code.get(key)
        ]

        # All sections run in parallel — total latency ≈ max(individual latencies)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        updated_code: Dict[str, Optional[str]] = {k: generated_code.get(k) for k in code_keys}
        errors = []
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                key, code = result
                updated_code[key] = code

        notes = f"AI errors on some sections: {'; '.join(errors)}" if errors else None

        return {
            "code": updated_code,
            "notes": notes,
            "model": resolved_model,
        }
