from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from services.odata_parser import ODataParser
from services.code_generator import CodeGenerator

app = FastAPI()
code_gen = CodeGenerator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FullCodeRequest(BaseModel):
    odata: Dict[str, Any]
    page_name: str
    entity_name: Optional[str] = None


class LinesCodeRequest(BaseModel):
    odata: Dict[str, Any]
    page_name: str
    entity_name: Optional[str] = None
    parent_entity: Optional[str] = None


@app.post("/generate-full")
async def generate_full_code(request: FullCodeRequest):
    try:
        # Parse OData
        parser = ODataParser(request.odata).parse()

        # Use provided entity name or derive from page name
        entity_name = request.entity_name or f"{request.page_name}Voucher"

        # Generate code
        generated_code = code_gen.generate_full_code(
            parser,
            request.page_name,
            entity_name
        )

        return {
            "success": True,
            "code": generated_code,
            "metadata": {
                "primary_key": parser.document_info['primary_key'],
                "user_filter_fields": [f['original_name'] for f in parser.document_info['user_filter_fields']],
                "datatable_fields": [f['original_name'] for f in parser.document_info['datatable_properties']]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate-lines")
async def generate_lines_code(request: LinesCodeRequest):
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

        return {
            "success": True,
            "code": generated_code
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))