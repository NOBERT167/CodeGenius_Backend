from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import traceback

from services.odata_parser import ODataParser
from services.code_generator import CodeGenerator

app = FastAPI(
    title="ASP.NET MVC Code Generator API",
    description="Generate complete ASP.NET MVC code from OData responses",
    version="1.0.0",
    docs_url="/docs",  # Enable docs at /docs
    redoc_url="/redoc"  # Enable redoc at /redoc
)

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

class FunctionHeaderRequest(BaseModel):
    function_definition: Dict[str, Any]
    page_name: str
    function_name: str

class FunctionLineRequest(BaseModel):
    function_definition: Dict[str, Any]
    page_name: str
    function_name: str
    parent_entity: str



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
                "primary_key": parser.document_info.get('primary_key'),
                "user_filter_fields": [f.get('original_name') for f in
                                       parser.document_info.get('user_filter_fields', [])],
                "datatable_fields": [f.get('original_name') for f in
                                     parser.document_info.get('datatable_properties', [])]
            }
        }

    except Exception as e:
        # Log the full traceback for debugging
        print(f"Error in generate-full: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating code: {str(e)}")


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
        # Log the full traceback for debugging
        print(f"Error in generate-lines: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating lines code: {str(e)}")

@app.post("/generate-function-header")
async def generate_function_header(request: FunctionHeaderRequest):
    try:
        # Generate header function code
        generated_code = code_gen.generate_function_header_code(
            request.function_definition,
            request.page_name,
            request.function_name
        )

        return {
            "success": True,
            "code": generated_code,
            "message": "Function header code generated successfully"
        }

    except Exception as e:
        print(f"Error in generate-function-header: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating function header code: {str(e)}")

@app.post("/generate-function-line")
async def generate_function_line(request: FunctionLineRequest):
    try:
        # Generate line function code
        generated_code = code_gen.generate_function_line_code(
            request.function_definition,
            request.page_name,
            request.function_name,
            request.parent_entity
        )

        return {
            "success": True,
            "code": generated_code,
            "message": "Function line code generated successfully"
        }

    except Exception as e:
        print(f"Error in generate-function-line: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error generating function line code: {str(e)}")


