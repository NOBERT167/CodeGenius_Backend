from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class FilterType(str, Enum):
    """Types of filters that can be applied"""
    DATE_RANGE = "date_range"
    APPROVAL_STATUS = "approval_status"
    CUSTOM = "custom"

class FilterConfig(BaseModel):
    """Configuration for individual filter"""
    type: FilterType
    field_name: str = Field(..., description="OData field name (e.g., 'Date', 'Approval_Status')")
    display_name: str = Field(..., description="Display name in UI (e.g., 'Date Range', 'Status')")
    default_value: Optional[str] = Field(None, description="Default filter value")
    options: Optional[List[Dict[str, str]]] = Field(None, description="Options for dropdown filters")
    enabled: bool = Field(True, description="Whether filter is enabled")

class FiltersConfiguration(BaseModel):
    """Complete filters configuration"""
    enabled: bool = Field(False, description="Whether to include filters in generated code")
    date_range_filter: Optional[FilterConfig] = None
    approval_status_filter: Optional[FilterConfig] = None
    custom_filters: Optional[List[FilterConfig]] = Field(default_factory=list)


class AIConfiguration(BaseModel):
    """Optional AI enhancement configuration for generated code"""
    enabled: bool = Field(False, description="Whether to apply AI enhancement after base generation")
    prompt: Optional[str] = Field(None, description="User instruction to refine generated code")
    model: Optional[str] = Field("gpt-4.1-mini", description="OpenAI model to use")
    temperature: float = Field(0.2, ge=0.0, le=1.0, description="Sampling temperature")
    max_output_tokens: int = Field(12000, ge=500, le=64000, description="Maximum output tokens")

class FullCodeRequest(BaseModel):
    odata: Dict[str, Any]
    page_name: str
    entity_name: Optional[str] = None
    filters: Optional[FiltersConfiguration] = Field(
        default_factory=lambda: FiltersConfiguration(enabled=False),
        description="Filter configuration (optional)"
    )
    ai: Optional[AIConfiguration] = Field(
        default_factory=lambda: AIConfiguration(enabled=False),
        description="AI enhancement configuration (optional)"
    )

class LinesCodeRequest(BaseModel):
    odata: Dict[str, Any]
    page_name: str
    entity_name: Optional[str] = None
    parent_entity: Optional[str] = None

class FunctionHeaderRequest(BaseModel):
    function_definition: str
    page_name: str
    function_name: str

class FunctionLineRequest(BaseModel):
    function_definition: str
    page_name: str
    function_name: str
    parent_entity: str