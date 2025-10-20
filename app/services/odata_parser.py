import re
from typing import Dict, Any, List
from datetime import datetime
import json


class ODataParser:
    def __init__(self, odata: Dict[str, Any]):
        self.odata = odata
        self.properties = []
        self.document_info = {}
        self.user_filter_fields = []

    def parse(self):
        """Enhanced parsing with pattern recognition"""
        try:
            for key, value in self.odata.items():
                prop = {
                    "original_name": key,
                    "csharp_name": self._normalize_property_name(key),
                    "display_name": self._format_label(key),
                    "type": self._infer_csharp_type(key, value),
                    "is_primary_key": self._is_primary_key(key),
                    "is_date": self._is_date_field(key, value),
                    "is_amount": self._is_amount_field(key),
                    "is_status": self._is_status_field(key),
                    "is_user_related": self._is_user_related(key),
                    "is_boolean": self._is_boolean_field(key, value),
                    "description": self._generate_description(key, value)
                }
                self.properties.append(prop)

            self._identify_document_structure()
            return self
        except Exception as e:
            raise Exception(f"Error parsing OData: {str(e)}")

    def _normalize_property_name(self, name: str) -> str:
        """Keep original names but make C# friendly"""
        # Remove special characters but keep underscores for JSON mapping
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        return clean_name

    def _infer_csharp_type(self, key: str, value: Any) -> str:
        """Smart type inference with proper boolean detection"""
        try:
            # First check if it's explicitly a boolean
            if self._is_boolean_field(key, value):
                return "bool"

            # Then check for date/time fields
            if self._is_date_field(key, value):
                return "DateTime"

            # Handle None values
            if value is None:
                return "object"

            # Handle string types
            if isinstance(value, str):
                # Check for date strings
                if re.match(r'^\d{4}-\d{2}-\d{2}', value) or 'date' in key.lower():
                    return "DateTime"
                # Check for time strings
                if re.match(r'^\d{2}:\d{2}:\d{2}', value) or 'time' in key.lower():
                    return "TimeSpan"
                return "string"

            # Handle numeric types
            elif isinstance(value, (int, float)):
                if self._is_amount_field(key):
                    return "decimal"
                # Check if it's actually a boolean represented as 0/1
                if value in [0, 1] and self._is_likely_boolean(key):
                    return "bool"
                return "int" if isinstance(value, int) else "decimal"

            # Handle boolean types
            elif isinstance(value, bool):
                return "bool"

            return "object"
        except Exception as e:
            print(f"Error inferring type for key '{key}', value '{value}': {e}")
            return "object"

    def _is_boolean_field(self, key: str, value: Any) -> bool:
        """Check if field is boolean based on name and value"""
        try:
            boolean_indicators = [
                'posted', 'closed', 'approved', 'rejected', 'completed',
                'active', 'enabled', 'locked', 'paid', 'processed',
                'is_', 'has_', 'allow_', 'enable_', 'disable_'
            ]

            # Check field name patterns
            key_lower = key.lower()
            name_suggests_boolean = any(indicator in key_lower for indicator in boolean_indicators)

            # Check value patterns
            value_suggests_boolean = (
                    isinstance(value, bool) or
                    (isinstance(value, (int, float)) and value in [0, 1]) or
                    (isinstance(value, str) and value.lower() in ['true', 'false', 'yes', 'no'])
            )

            return name_suggests_boolean or value_suggests_boolean
        except:
            return False

    def _is_likely_boolean(self, key: str) -> bool:
        """Check if field name suggests it's a boolean (for 0/1 values)"""
        try:
            boolean_indicators = [
                'posted', 'closed', 'approved', 'rejected', 'completed',
                'active', 'enabled', 'locked', 'paid', 'processed',
                'is_', 'has_', 'allow_', 'enable_', 'disable_'
            ]
            return any(indicator in key.lower() for indicator in boolean_indicators)
        except:
            return False

    def _is_primary_key(self, key: str) -> bool:
        try:
            primary_indicators = ['no', 'code', 'id', 'docno', 'number', 'key']
            return any(indicator in key.lower() for indicator in primary_indicators)
        except:
            return False

    def _is_date_field(self, key: str, value: Any) -> bool:
        try:
            date_indicators = ['date', 'time', 'created', 'modified', 'start', 'end']
            if isinstance(value, str):
                # Check for common date patterns
                date_patterns = [
                    r'^\d{4}-\d{2}-\d{2}',
                    r'^\d{2}/\d{2}/\d{4}',
                    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
                ]
                if any(re.match(pattern, value) for pattern in date_patterns):
                    return True
            return any(indicator in key.lower() for indicator in date_indicators)
        except:
            return False

    def _is_amount_field(self, key: str) -> bool:
        try:
            amount_indicators = ['amount', 'total', 'cost', 'price', 'value', 'sum', 'balance']
            return any(indicator in key.lower() for indicator in amount_indicators)
        except:
            return False

    def _is_status_field(self, key: str) -> bool:
        try:
            return 'status' in key.lower()
        except:
            return False

    def _is_user_related(self, key: str) -> bool:
        try:
            user_indicators = ['user', 'createdby', 'requestor', 'staff', 'employee', 'account', 'personnel']
            return any(indicator in key.lower() for indicator in user_indicators)
        except:
            return False

    def _generate_description(self, key: str, value: Any) -> str:
        """Generate meaningful descriptions for properties"""
        try:
            if self._is_primary_key(key):
                return "Primary key identifier"
            elif self._is_date_field(key, value):
                return "Date field"
            elif self._is_amount_field(key):
                return "Monetary amount"
            elif self._is_status_field(key):
                return "Document status"
            elif self._is_boolean_field(key, value):
                return "Boolean indicator"
            return ""
        except:
            return ""

    def _identify_document_structure(self):
        """Identify document metadata for code generation"""
        try:
            # Find primary key
            primary_keys = [p for p in self.properties if p.get('is_primary_key')]
            self.document_info['primary_key'] = primary_keys[0] if primary_keys else None

            # Find user filter fields
            self.document_info['user_filter_fields'] = [
                p for p in self.properties if p.get('is_user_related')
            ]

            # Find important properties for datatable
            self.document_info['datatable_properties'] = self._select_datatable_properties()
        except Exception as e:
            print(f"Error in document structure identification: {e}")
            self.document_info['primary_key'] = None
            self.document_info['user_filter_fields'] = []
            self.document_info['datatable_properties'] = []

    def _select_datatable_properties(self, max_count=8) -> List[Dict]:
        """Select most important properties for datatable display"""
        try:
            priority_properties = []

            # Always include primary key
            if self.document_info.get('primary_key'):
                priority_properties.append(self.document_info['primary_key'])

            # Include dates
            date_props = [p for p in self.properties if p.get('is_date')]
            priority_properties.extend(date_props[:2])  # Max 2 dates

            # Include amounts
            amount_props = [p for p in self.properties if p.get('is_amount')]
            priority_properties.extend(amount_props[:2])  # Max 2 amounts

            # Include status
            status_props = [p for p in self.properties if p.get('is_status')]
            priority_properties.extend(status_props[:1])

            # Include booleans (limit to 1)
            boolean_props = [p for p in self.properties if p.get('is_boolean')]
            priority_properties.extend(boolean_props[:1])

            # Fill remaining slots with other properties
            remaining_slots = max_count - len(priority_properties)
            if remaining_slots > 0:
                other_props = [p for p in self.properties
                               if p not in priority_properties
                               and not p.get('is_primary_key')]
                priority_properties.extend(other_props[:remaining_slots])

            return priority_properties[:max_count]
        except Exception as e:
            print(f"Error selecting datatable properties: {e}")
            # Return first few properties as fallback
            return self.properties[:min(max_count, len(self.properties))]

    def _format_label(self, property_name: str) -> str:
        """Convert Property_Name to Property Name"""
        try:
            # Replace underscores with spaces and capitalize each word
            return ' '.join(word.capitalize() for word in property_name.split('_'))
        except:
            return property_name