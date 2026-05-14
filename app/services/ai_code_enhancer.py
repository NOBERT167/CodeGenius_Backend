import asyncio
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

_SECTION_LABELS = {
    "model": "C# ViewModel class",
    "controller": "C# MVC Controller",
    "main_view": "Razor main/index view (.cshtml)",
    "list_view": "Razor list partial view (.cshtml)",
    "document_view": "Razor document detail view (.cshtml)",
}

_FUNCTION_SECTION_LABELS = {
    "model": "C# ViewModel class",
    "controller": "C# MVC Controller action methods",
    "view": "Razor form partial view (.cshtml)",
    "javascript": "JavaScript / jQuery AJAX submission code",
    "controller_methods": "C# MVC Controller action methods",
    "partial_view": "Razor form partial view (.cshtml)",
}

# Rich project context injected into every function-code AI call so the AI
# understands the codebase conventions without needing extra explanation.
_PROJECT_CONTEXT = """
PROJECT CONTEXT — ASP.NET MVC 5 + Microsoft Dynamics Business Central:

1. OData Data Access Pattern:
   All OData calls use Credentials.GetOdataData(endpoint) which returns an HttpWebResponse.
   Standard pattern to populate a dropdown list from an OData page:

       var myList = new List<SelectListItem>();
       var httpResp = Credentials.GetOdataData("ODataPageName?$select=No,Description");
       using (var sr = new StreamReader(httpResp.GetResponseStream()))
       {
           var details = JObject.Parse(sr.ReadToEnd());
           myList.AddRange(
               from JObject item in details["value"]
               select new SelectListItem
               {
                   Text = $"{(string)item["No"]} - {(string)item["Description"]}",
                   Value = (string)item["No"]
               });
       }
       viewModel.MyFieldList = myList;

   ViewModel property: public List<SelectListItem> MyFieldList { get; set; }
   View usage: @Html.DropDownListFor(m => m.MyField, Model.MyFieldList, "-- Select --",
                   new { @class = "form-control select2" })

2. Session Variables (Logged-in User):
   The following session variables are ALWAYS available in every controller action:

       var employee = Session["EmployeeData"] as EmployeeView;
       var staffNo   = Session["Username"].ToString();          // Employee No / staff number
       var userId    = employee?.UserID;                        // Login / User ID
       var department = employee?.GlobalDimension1Code;         // Department / Global Dim 1
       var employeeName = employee?.Name;                       // Full name

   When an instruction says any of:
     "don't add [field] to the view"
     "pass [field] from session / logged-in user"
     "use the logged-in user's [field]"
     "pass staffNo / employeeNo / userId / department from the session"
   Then:
     a) Do NOT render that field as a form input in the view (no TextBoxFor / DropDownListFor).
     b) In the controller POST action, read the value from session (as above)
        and pass it directly as a parameter to the BC function call.
     c) Remove any corresponding ViewModel property that would just duplicate session data.

3. BC Enum (Static) Dropdowns:
   BC enum option values are integers, typically starting from 0 OR from 1 (developer choice).
   Build the list inline:

       viewModel.SeverityList = new SelectList(new List<SelectListItem>
       {
           new SelectListItem { Text = "Minor",    Value = "1" },
           new SelectListItem { Text = "Moderate", Value = "2" },
           new SelectListItem { Text = "Severe",   Value = "3" },
       }, "Value", "Text");

   ViewModel property: public SelectList SeverityList { get; set; }
   View usage: @Html.DropDownListFor(m => m.Severity, Model.SeverityList, "-- Select --",
                   new { @class = "form-control select2" })

4. Select2 Dropdowns:
   ALL dropdown selects must carry the CSS class "form-control select2".
   The shared layout already initialises Select2, so just ensure the class is present.

5. General Conventions:
   - Check Session["Username"] == null at the start of every GET/POST action and redirect to Login if null.
   - Wrap controller bodies in try/catch; on exception return the shared error partial view.
   - Use PartialView(...) not View(...) for modal/inline forms.
"""


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

    async def enhance_function_code(
        self,
        generated_code: Dict[str, Optional[str]],
        page_name: str,
        function_name: str,
        style_prompt: Optional[str],
        dropdown_fields: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Refine function-header or function-line generated code in parallel.
        Applies form styling, dropdown conversions, and session-based field passthrough.
        """
        if not self.is_available():
            raise ValueError("OPENAI_API_KEY is not configured on the server")

        # Build a rich dropdown description the AI can act on
        dropdown_desc = ""
        if dropdown_fields:
            parts = []
            for df in dropdown_fields:
                fname = df.get("field_name", "")
                dd_type = df.get("type", "static")

                if dd_type == "odata":
                    endpoint = df.get("odata_endpoint", "")
                    text_tmpl = df.get("odata_text_template", "")
                    value_fld = df.get("odata_value_field", "")
                    desc = (
                        f"  - {fname}: OData dropdown — "
                        f"endpoint: \"{endpoint}\", "
                        f"text template: \"{text_tmpl or '{No} - {Description}'}\", "
                        f"value field: \"{value_fld or 'No'}\". "
                        f"Use Credentials.GetOdataData pattern (see project context)."
                    )
                else:
                    opts = df.get("options", [])
                    if opts:
                        opts_str = ", ".join(
                            f"{o.get('text', '')} (value: {o.get('value', o.get('text', ''))})"
                            for o in opts
                        )
                        desc = f"  - {fname}: static dropdown with options [{opts_str}]"
                    else:
                        desc = f"  - {fname}: static dropdown — infer sensible options from field name/context"
                parts.append(desc)

            dropdown_desc = (
                "Convert these fields from text inputs to dropdowns:\n"
                + "\n".join(parts)
                + "\n\nFor OData dropdowns follow the Credentials.GetOdataData pattern in the project context.\n"
                  "For static dropdowns build a SelectList inline in the controller.\n"
                  "All dropdowns must have CSS class \"form-control select2\"."
            )

        style_desc = style_prompt.strip() if style_prompt and style_prompt.strip() else ""

        resolved_model = self.default_model

        client_kwargs: Dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = AsyncOpenAI(**client_kwargs)

        async def _enhance_section(section_key: str, section_code: str) -> tuple[str, str]:
            label = _FUNCTION_SECTION_LABELS.get(section_key, section_key)
            is_view = section_key in ("view", "partial_view")
            is_model = section_key == "model"
            is_controller = section_key in ("controller", "controller_methods")

            if is_view:
                extra = []
                if style_desc:
                    extra.append(f"Form styling: {style_desc}")
                if dropdown_desc:
                    extra.append(dropdown_desc)
                specific = (
                    "\n\n".join(extra)
                    if extra
                    else "Improve layout, spacing, and accessibility without changing behaviour."
                )
            elif is_model and dropdown_fields:
                odata_fields = [
                    df.get("field_name", "") for df in dropdown_fields
                    if df.get("type", "static") == "odata"
                ]
                static_fields = [
                    df.get("field_name", "") for df in dropdown_fields
                    if df.get("type", "static") == "static"
                ]
                parts = []
                if odata_fields:
                    parts.append(
                        f"Add public List<SelectListItem> properties for OData dropdowns: {', '.join(odata_fields)}. "
                        f"Name each <FieldName>List (e.g., PropertyNoList)."
                    )
                if static_fields:
                    parts.append(
                        f"Add public SelectList properties for static dropdowns: {', '.join(static_fields)}. "
                        f"Name each <FieldName>List (e.g., SeverityList)."
                    )
                specific = " ".join(parts) if parts else "Improve clarity and null safety."
            elif is_controller and (dropdown_fields or style_desc):
                extra = []
                if dropdown_desc:
                    extra.append(
                        dropdown_desc
                        + "\nIn GET action: populate each list and assign to viewModel.<FieldName>List before returning."
                    )
                if style_desc:
                    extra.append(f"Context (for reference only): {style_desc}")
                specific = "\n\n".join(extra) if extra else "Improve null safety and validation."
            else:
                specific = "Improve code clarity, null safety, and validation without changing behaviour."

            system_msg = (
                f"You are an expert C# ASP.NET MVC 5 code assistant.\n"
                f"{_PROJECT_CONTEXT}\n"
                f"---\n"
                f"You will receive one {label} file for page '{page_name}', function '{function_name}'.\n"
                f"Apply the task below, then return ONLY the improved code — "
                f"no explanation, no markdown fences.\n"
                f"Preserve all existing endpoint names, method signatures, and architecture.\n\n"
                f"Task: {specific}"
            )
            response = await client.chat.completions.create(
                model=resolved_model,
                temperature=0.2,
                max_tokens=4000,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": section_code},
                ],
            )
            refined = response.choices[0].message.content
            return section_key, (refined.strip() if refined else section_code)

        # All present sections in parallel
        tasks = [
            _enhance_section(key, generated_code[key])
            for key in generated_code
            if generated_code.get(key)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        updated_code: Dict[str, Optional[str]] = dict(generated_code)
        errors = []
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                key, code = result
                updated_code[key] = code

        notes = f"AI errors: {'; '.join(errors)}" if errors else None

        return {
            "code": updated_code,
            "notes": notes,
            "model": resolved_model,
        }
