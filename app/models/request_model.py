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
    """AI enhancement for full MVC generation"""
    enabled: bool = Field(False, description="Whether to apply AI enhancement after base generation")
    prompt: Optional[str] = Field(None, description="User instruction to refine generated code")


class DropdownField(BaseModel):
    """A form field that should be rendered as a dropdown"""
    field_name: str = Field(..., description="Parameter/field name as it appears in the function definition")
    type: str = Field(
        "static",
        description="'static' for hardcoded options (NAV enums), 'odata' for OData-fetched list"
    )
    # --- Static dropdown fields ---
    options: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description="For type='static': list of {text, value} pairs. Values are typically integers as strings."
    )
    # --- OData dropdown fields ---
    odata_endpoint: Optional[str] = Field(
        None,
        description="For type='odata': OData page/filter, e.g. \"FixedAssetsList?$filter=Asset_Type eq 'Property'\""
    )
    odata_text_template: Optional[str] = Field(
        None,
        description="For type='odata': text template using field names in braces, e.g. '{No} - {Description}'"
    )
    odata_value_field: Optional[str] = Field(
        None,
        description="For type='odata': the OData field used as the option value, e.g. 'No'"
    )


class FunctionAIConfiguration(BaseModel):
    """AI enhancement for function-header and function-line generation"""
    enabled: bool = Field(False)
    style_prompt: Optional[str] = Field(
        None,
        description="Describe how the form should look, e.g. 'Use Bootstrap card with blue header and two-column layout'"
    )
    dropdown_fields: Optional[List[DropdownField]] = Field(
        default_factory=list,
        description="Fields that should be rendered as dropdowns instead of text inputs"
    )

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
    ai: Optional[FunctionAIConfiguration] = Field(
        default_factory=lambda: FunctionAIConfiguration(enabled=False)
    )

class FunctionLineRequest(BaseModel):
    function_definition: str
    page_name: str
    function_name: str
    parent_entity: str
    ai: Optional[FunctionAIConfiguration] = Field(
        default_factory=lambda: FunctionAIConfiguration(enabled=False)
    )