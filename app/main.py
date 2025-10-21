from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import traceback

from app.services.odata_parser import ODataParser
from app.services.code_generator import CodeGenerator

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

# For IIS deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info"
    )

