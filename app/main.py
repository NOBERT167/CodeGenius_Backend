from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import traceback
import threading
import json
from pathlib import Path

from app.services.odata_parser import ODataParser
from app.services.code_generator import CodeGeneratorWithFilters
from app.services.ai_code_enhancer import AICodeEnhancer
from app.models.request_model import (
    FullCodeRequest,
    LinesCodeRequest,
    FunctionHeaderRequest,
    FunctionLineRequest,
    FiltersConfiguration
)

# ---------------------------------------------------------------------------
# Persistent generation stats — stored in stats.json next to this file
# Files-per-generation: full=5, lines=4, function-header=4, function-line=4
# ---------------------------------------------------------------------------
_STATS_FILE = Path(__file__).parent.parent / "stats.json"

_FILES_PER_TYPE: Dict[str, int] = {
    "full": 5,            # model, controller, main_view, list_view, document_view
    "lines": 4,           # model, controller, partial_view, javascript
    "function_header": 4, # model, controller, view, javascript
    "function_line": 4,   # model, controller_methods, partial_view, javascript
}

_STATS_DEFAULTS: Dict[str, int] = {
    "full_generations": 0,
    "lines_generations": 0,
    "function_header_generations": 0,
    "function_line_generations": 0,
    "total_generations": 0,
    "total_files_generated": 0,
}

_stats_lock = threading.Lock()


def _load_stats() -> Dict[str, int]:
    """Load stats from disk, filling in any missing keys with defaults."""
    if _STATS_FILE.exists():
        try:
            data = json.loads(_STATS_FILE.read_text(encoding="utf-8"))
            # Merge with defaults so new keys added in future don't break
            return {**_STATS_DEFAULTS, **{k: int(v) for k, v in data.items() if k in _STATS_DEFAULTS}}
        except Exception:
            pass
    return dict(_STATS_DEFAULTS)


def _save_stats(stats: Dict[str, int]) -> None:
    """Write stats atomically to disk (write temp file then replace)."""
    try:
        tmp = _STATS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        tmp.replace(_STATS_FILE)
    except Exception:
        pass  # Never let a stats write failure crash a generation request


_stats: Dict[str, int] = _load_stats()


def _record_generation(gen_type: str) -> None:
    files = _FILES_PER_TYPE.get(gen_type, 1)
    with _stats_lock:
        _stats[f"{gen_type}_generations"] += 1
        _stats["total_generations"] += 1
        _stats["total_files_generated"] += files
        _save_stats(_stats)

app = FastAPI(
    title="ASP.NET MVC Code Generator API with Filters",
    description="Generate complete ASP.NET MVC code from OData responses with optional filters",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

code_gen = CodeGeneratorWithFilters()
ai_enhancer = AICodeEnhancer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "ASP.NET MVC Code Generator API",
        "version": "3.0.0",
        "features": [
            "Full MVC code generation",
            "Lines code generation",
            "Function header code generation",
            "Function line code generation",
            "Optional date range filters",
            "Optional approval status filters",
            "Custom filters support"
        ],
        "endpoints": {
            "generate_full": "/generate-full",
            "generate_lines": "/generate-lines",
            "generate_function_header": "/generate-function-header",
            "generate_function_line": "/generate-function-line"
        }
    }


@app.post("/generate-full")
async def generate_full_code(request: FullCodeRequest):
    """
    Generate complete MVC code with optional filters

    Example request body:
    {
        "odata": {...},
        "page_name": "ExpenseRequisition",
        "entity_name": "ExpenseRequisitionCard",
        "filters": {
            "enabled": true,
            "date_range_filter": {
                "type": "date_range",
                "field_name": "Date",
                "display_name": "Date Range",
                "enabled": true
            },
            "approval_status_filter": {
                "type": "approval_status",
                "field_name": "Approval_Status",
                "display_name": "Approval Status",
                "default_value": "Open",
                "options": [
                    {"text": "Open", "value": "Open"},
                    {"text": "Pending Approval", "value": "Pending Approval"},
                    {"text": "Approved", "value": "Approved"}
                ],
                "enabled": true
            }
        }
    }
    """
    try:
        # Parse OData
        parser = ODataParser(request.odata).parse()

        # Use provided entity name or derive from page name
        entity_name = request.entity_name or f"{request.page_name}Voucher"

        # Convert Pydantic model to dict for code generator
        filters_config = None
        if request.filters and request.filters.enabled:
            filters_config = {
                'enabled': request.filters.enabled,
                'date_range_filter': request.filters.date_range_filter.dict() if request.filters.date_range_filter else None,
                'approval_status_filter': request.filters.approval_status_filter.dict() if request.filters.approval_status_filter else None,
                'custom_filters': [f.dict() for f in
                                   request.filters.custom_filters] if request.filters.custom_filters else []
            }

        # Generate code
        generated_code = code_gen.generate_full_code(
            parser,
            request.page_name,
            entity_name,
            filters_config
        )

        ai_enabled = bool(request.ai and request.ai.enabled)
        ai_applied = False
        ai_notes = None
        ai_model = None

        if ai_enabled:
            parser_summary = {
                "properties": parser.properties,
                "primary_key": parser.document_info.get('primary_key'),
                "user_filter_fields": parser.document_info.get('user_filter_fields', []),
                "datatable_properties": parser.document_info.get('datatable_properties', [])
            }

            enhanced_result = await ai_enhancer.enhance_full_code(
                generated_code=generated_code,
                page_name=request.page_name,
                entity_name=entity_name,
                parser_summary=parser_summary,
                user_prompt=request.ai.prompt if request.ai else None,
            )

            generated_code = enhanced_result["code"]
            ai_notes = enhanced_result.get("notes")
            ai_model = enhanced_result.get("model")
            ai_applied = True

        _record_generation("full")
        return {
            "success": True,
            "code": generated_code,
            "metadata": {
                "user_filter_fields": [f.get('original_name') for f in
                                       parser.document_info.get('user_filter_fields', [])],
                "datatable_fields": [f.get('original_name') for f in
                                     parser.document_info.get('datatable_properties', [])],
                "filters_enabled": request.filters.enabled if request.filters else False,
                "ai_applied": ai_applied,
                "ai_notes": ai_notes,
                "ai_model": ai_model,
            },
            "message": "Code generated successfully with" + (" filters" if filters_config else "out filters")
        }

    except Exception as e:
        print(f"Error in generate-full: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating code: {str(e)}")


@app.post("/generate-lines")
async def generate_lines_code(request: LinesCodeRequest):
    """Generate lines code only (no filter support for lines)"""
    try:
        # Parse OData for lines
        parser = ODataParser(request.odata).parse()

        # Use provided names or derive defaults
        entity_name = request.entity_name or f"{request.page_name}Lines"
        parent_entity = request.parent_entity or request.page_name

        # Generate lines code only
        generated_code = code_gen.generate_lines_code(
            parser,
            request.page_name,
            entity_name,
            parent_entity
        )

        _record_generation("lines")
        return {
            "success": True,
            "code": generated_code,
            "message": "Lines code generated successfully"
        }

    except Exception as e:
        print(f"Error in generate-lines: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating lines code: {str(e)}")


@app.post("/generate-function-header")
async def generate_function_header(request: FunctionHeaderRequest):
    """Generate function header code"""
    try:
        # Validate XML is not empty
        if not request.function_definition.strip():
            raise HTTPException(status_code=400, detail="Function definition XML cannot be empty")

        # Basic XML validation
        if not request.function_definition.strip().startswith('<'):
            raise HTTPException(status_code=400, detail="Invalid XML format")

        # Generate code
        generated_code = code_gen.generate_function_header_code(
            request.function_definition,
            request.page_name,
            request.function_name
        )

        ai_applied = False
        ai_notes = None
        ai_model = None

        if request.ai and request.ai.enabled:
            dropdown_dicts = [
                df.dict() for df in request.ai.dropdown_fields
            ] if request.ai.dropdown_fields else []

            enhanced_result = await ai_enhancer.enhance_function_code(
                generated_code=generated_code,
                page_name=request.page_name,
                function_name=request.function_name,
                style_prompt=request.ai.style_prompt,
                dropdown_fields=dropdown_dicts,
            )
            generated_code = enhanced_result["code"]
            ai_notes = enhanced_result.get("notes")
            ai_model = enhanced_result.get("model")
            ai_applied = True

        _record_generation("function_header")
        return {
            "success": True,
            "code": generated_code,
            "metadata": {
                "ai_applied": ai_applied,
                "ai_notes": ai_notes,
                "ai_model": ai_model,
            },
            "message": "Function header code generated successfully"
        }

    except Exception as e:
        print(f"Error in generate-function-header: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating function header code: {str(e)}")


@app.post("/generate-function-line")
async def generate_function_line(request: FunctionLineRequest):
    """Generate function line code"""
    try:
        # Generate line function code
        generated_code = code_gen.generate_function_line_code(
            request.function_definition,
            request.page_name,
            request.function_name,
            request.parent_entity
        )

        ai_applied = False
        ai_notes = None
        ai_model = None

        if request.ai and request.ai.enabled:
            dropdown_dicts = [
                df.dict() for df in request.ai.dropdown_fields
            ] if request.ai.dropdown_fields else []

            enhanced_result = await ai_enhancer.enhance_function_code(
                generated_code=generated_code,
                page_name=request.page_name,
                function_name=request.function_name,
                style_prompt=request.ai.style_prompt,
                dropdown_fields=dropdown_dicts,
            )
            generated_code = enhanced_result["code"]
            ai_notes = enhanced_result.get("notes")
            ai_model = enhanced_result.get("model")
            ai_applied = True

        _record_generation("function_line")
        return {
            "success": True,
            "code": generated_code,
            "metadata": {
                "ai_applied": ai_applied,
                "ai_notes": ai_notes,
                "ai_model": ai_model,
            },
            "message": "Function line code generated successfully"
        }

    except Exception as e:
        print(f"Error in generate-function-line: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating function line code: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Return cumulative generation stats for the current server session."""
    with _stats_lock:
        snapshot = dict(_stats)
    return {
        "total_generations": snapshot["total_generations"],
        "total_files_generated": snapshot["total_files_generated"],
        "by_type": {
            "full": {
                "generations": snapshot["full_generations"],
                "files": snapshot["full_generations"] * _FILES_PER_TYPE["full"],
            },
            "lines": {
                "generations": snapshot["lines_generations"],
                "files": snapshot["lines_generations"] * _FILES_PER_TYPE["lines"],
            },
            "function_header": {
                "generations": snapshot["function_header_generations"],
                "files": snapshot["function_header_generations"] * _FILES_PER_TYPE["function_header"],
            },
            "function_line": {
                "generations": snapshot["function_line_generations"],
                "files": snapshot["function_line_generations"] * _FILES_PER_TYPE["function_line"],
            },
        },
        "note": f"Stats are persisted to {_STATS_FILE.name} and survive server restarts.",
    }


@app.get("/filter-examples")
async def get_filter_examples():
    """Get example filter configurations"""
    return {
        "basic_filters": {
            "enabled": True,
            "date_range_filter": {
                "type": "date_range",
                "field_name": "Date",
                "display_name": "Date Range",
                "enabled": True
            },
            "approval_status_filter": {
                "type": "approval_status",
                "field_name": "Approval_Status",
                "display_name": "Approval Status",
                "default_value": "Open",
                "options": [
                    {"text": "Open", "value": "Open"},
                    {"text": "Pending Approval", "value": "Pending Approval"},
                    {"text": "Approved", "value": "Approved"},
                    {"text": "Open & Pending", "value": "Open,Pending Approval"}
                ],
                "enabled": True
            }
        },
        "with_custom_filters": {
            "enabled": True,
            "date_range_filter": {
                "type": "date_range",
                "field_name": "Posting_Date",
                "display_name": "Posting Date",
                "enabled": True
            },
            "approval_status_filter": {
                "type": "approval_status",
                "field_name": "Status",
                "display_name": "Document Status",
                "default_value": "Open",
                "enabled": True
            },
            "custom_filters": [
                {
                    "type": "custom",
                    "field_name": "Department_Code",
                    "display_name": "Department",
                    "options": [
                        {"text": "Finance", "value": "FIN"},
                        {"text": "HR", "value": "HR"},
                        {"text": "IT", "value": "IT"}
                    ],
                    "enabled": True
                },
                {
                    "type": "custom",
                    "field_name": "Project_Code",
                    "display_name": "Project",
                    "enabled": True
                }
            ]
        },
        "no_filters": {
            "enabled": False
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info"
    )