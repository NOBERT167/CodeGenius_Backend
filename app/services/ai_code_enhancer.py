import json
import os
from typing import Any, Dict, Optional

from openai import OpenAI


class AICodeEnhancer:
    """Enhances generated code by applying user instructions with OpenAI."""

    def __init__(self):
        # self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_key = "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"
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def enhance_full_code(
        self,
        generated_code: Dict[str, Optional[str]],
        page_name: str,
        entity_name: str,
        parser_summary: Dict[str, Any],
        user_prompt: Optional[str],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 12000,
    ) -> Dict[str, Any]:
        if not self.is_available():
            raise ValueError("OPENAI_API_KEY is not configured on the server")

        instruction = (
            user_prompt.strip()
            if user_prompt and user_prompt.strip()
            else "Improve maintainability, naming clarity, null safety, and validation without changing behavior."
        )

        system_prompt = (
            "You are an expert C# ASP.NET MVC code assistant. "
            "You will receive generated code parts. Return JSON only with keys: "
            "model, controller, main_view, list_view, document_view, notes. "
            "Keep existing architecture and endpoint names. "
            "Do not remove required code paths. "
            "If a section should remain unchanged, return the original content for that section."
        )

        user_content = {
            "task": "Refine generated MVC code",
            "page_name": page_name,
            "entity_name": entity_name,
            "instruction": instruction,
            "parser_summary": parser_summary,
            "generated_code": generated_code,
        }

        client_kwargs: Dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model=model or self.default_model,
            temperature=temperature,
            max_tokens=max_output_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content)},
            ],
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response")

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"OpenAI returned invalid JSON: {str(exc)}") from exc

        updated_code: Dict[str, Optional[str]] = {}
        code_keys = ["model", "controller", "main_view", "list_view", "document_view"]

        for key in code_keys:
            candidate = parsed.get(key)
            if candidate is None:
                updated_code[key] = generated_code.get(key)
            else:
                updated_code[key] = str(candidate)

        notes = parsed.get("notes")

        return {
            "code": updated_code,
            "notes": str(notes) if notes is not None else None,
            "model": model or self.default_model,
        }
