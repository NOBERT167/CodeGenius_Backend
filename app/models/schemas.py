from pydantic import BaseModel

class CodeGenerationRequest(BaseModel):
    odata: dict
    page_name: str
    options: dict = {}

class GeneratedCode(BaseModel):
    model: str
    controller: str
    view: str