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

    def _format_label(self, property_name: str) -> str:
        """Convert Property_Name to Property Name"""
        try:
            # Replace underscores with spaces and capitalize each word
            return ' '.join(word.capitalize() for word in property_name.split('_'))
        except:
            return property_name

    def _infer_csharp_type(self, key: str, value: Any) -> str:
        """Smart type inference with better detection logic"""
        try:
            # Handle None values first
            if value is None:
                return "object"

            # Handle actual boolean types
            if isinstance(value, bool):
                return "bool"

            # Handle string types
            if isinstance(value, str):
                # Check for time-only strings (HH:MM:SS)
                if self._is_time_string(value):
                    return "TimeSpan"

                # Check for date strings (more strict checking)
                if self._is_definitely_date_string(key, value):
                    return "DateTime"

                # Check for boolean strings
                if value.lower() in ['true', 'false', 'yes', 'no']:
                    return "bool"

                # Default for strings
                return "string"

            # Handle numeric types
            elif isinstance(value, (int, float)):
                # Check for amounts/money fields
                if self._is_amount_field(key):
                    return "decimal"

                # Check for boolean-like integers (only if field name strongly suggests boolean)
                if value in [0, 1] and self._is_strong_boolean_indicator(key):
                    return "bool"

                # Default for integers
                return "int" if isinstance(value, int) else "decimal"

            return "object"
        except Exception as e:
            print(f"Error inferring type for {key}: {value} - {e}")
            return "object"

    def _is_definitely_boolean(self, key: str, value: Any) -> bool:
        """Strict boolean detection"""
        # Strong boolean indicators in field names
        strong_boolean_indicators = [
            'is_', 'has_', 'can_', 'should_', 'will_', 'was_', 'were_',
            'allow_', 'enable_', 'disable_', 'active', 'enabled', 'disabled',
            'visible', 'hidden', 'locked', 'approved', 'rejected', 'published',
            'completed', 'closed', 'posted', 'processed'
        ]

        key_lower = key.lower()

        # If field name strongly suggests boolean
        name_suggests_boolean = any(indicator in key_lower for indicator in strong_boolean_indicators)

        # Value must clearly be boolean
        value_is_boolean = (
                isinstance(value, bool) or
                (isinstance(value, (int, float)) and value in [0, 1]) or
                (isinstance(value, str) and value.lower() in ['true', 'false', 'yes', 'no', 'y', 'n'])
        )

        return name_suggests_boolean and value_is_boolean

    def _is_strong_boolean_indicator(self, key: str) -> bool:
        """Check if field name strongly suggests it's a boolean"""
        strong_indicators = [
            'is_', 'has_', 'can_', 'should_', 'will_', 'was_', 'were_',
            'allow_', 'enable_', 'disable_', 'active', 'enabled', 'disabled'
        ]
        return any(indicator in key.lower() for indicator in strong_indicators)

    def _is_time_string(self, value: str) -> bool:
        """Check if string represents only time (HH:MM:SS)"""
        if not isinstance(value, str):
            return False

        # Match time patterns like "08:00:00", "14:30", "23:59:59"
        time_patterns = [
            r'^\d{1,2}:\d{2}:\d{2}$',  # HH:MM:SS
            r'^\d{1,2}:\d{2}$',  # HH:MM
        ]

        return any(re.match(pattern, value) for pattern in time_patterns)

    def _is_definitely_date_string(self, key: str, value: str) -> bool:
        """Strict date string detection"""
        if not isinstance(value, str):
            return False

        # Date-specific field names
        date_field_indicators = ['date', 'created', 'modified', 'start', 'end', 'expir']
        key_lower = key.lower()

        # Field name must suggest it's a date
        name_suggests_date = any(indicator in key_lower for indicator in date_field_indicators)

        if not name_suggests_date:
            return False

        # Strict date patterns (must match exactly)
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # YYYY-MM-DDTHH:MM:SS
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
        ]

        return any(re.match(pattern, value) for pattern in date_patterns)

    def _is_boolean_field(self, key: str, value: Any) -> bool:
        """Legacy method for compatibility"""
        return self._is_definitely_boolean(key, value)

    def _is_primary_key(self, key: str) -> bool:
        try:
            primary_indicators = ['no', 'code', 'id', 'docno', 'number', 'key']
            return any(indicator in key.lower() for indicator in primary_indicators)
        except:
            return False

    def _is_date_field(self, key: str, value: Any) -> bool:
        """For description purposes only"""
        try:
            date_indicators = ['date', 'time', 'created', 'modified', 'start', 'end']
            if isinstance(value, str):
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
            amount_indicators = ['amount', 'total', 'cost', 'price', 'value', 'sum', 'balance', 'qty', 'quantity']
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
                if self._is_time_string(str(value)):
                    return "Time field"
                return "Date field"
            elif self._is_amount_field(key):
                return "Monetary amount"
            elif self._is_status_field(key):
                return "Document status"
            elif self._is_boolean_field(key, value):
                return "Boolean indicator"
            elif self._is_user_related(key):
                return "User reference"
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

    def parse_function_parameters(self, function_definition):
        """Parse SOAP function parameters with enhanced detection"""
        parameters = []

        try:
            # Handle different XML structure formats
            complex_type = function_definition.get('complexType', {})
            sequence = complex_type.get('sequence', {})
            elements = sequence.get('element', [])

            if not isinstance(elements, list):
                elements = [elements]

            for element in elements:
                # Handle both dictionary and string element formats
                if isinstance(element, dict):
                    param_name = element.get('@name', '')
                    param_type = element.get('@type', 'string')
                    min_occurs = element.get('@minOccurs', '1')
                else:
                    # If element is a string, use it as name with default type
                    param_name = element
                    param_type = 'string'
                    min_occurs = '1'

                if param_name:  # Only process if we have a name
                    csharp_type = self._map_xml_type_to_csharp(param_type)

                    parameters.append({
                        'name': param_name,
                        'original_name': param_name,
                        'csharp_name': self._normalize_function_param_name(param_name),
                        'display_name': self._format_function_display_name(param_name),
                        'type': csharp_type,
                        'xml_type': param_type,
                        'is_required': min_occurs == '1',
                        'is_dropdown': self._is_dropdown_field(param_name),
                        'is_date': csharp_type == 'DateTime',
                        'is_amount': self._is_amount_field(param_name)
                    })

        except Exception as e:
            print(f"Error parsing function parameters: {e}")

        return parameters

    def _normalize_function_param_name(self, name):
        """Normalize function parameter names to C# property convention"""
        # Remove special characters and capitalize each word
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        return ''.join(word.capitalize() for word in clean_name.split('_'))

    def _format_function_display_name(self, name):
        """Format function parameter name for display"""
        return ' '.join(word.capitalize() for word in name.split('_'))

    def _map_xml_type_to_csharp(self, xml_type):
        """Map XML schema types to C# types with more comprehensive mapping"""
        type_mapping = {
            'string': 'string',
            'decimal': 'decimal',
            'int': 'int',
            'integer': 'int',
            'boolean': 'bool',
            'date': 'DateTime',
            'datetime': 'DateTime',
            'double': 'double',
            'float': 'float',
            'long': 'long',
            'short': 'short',
            'byte': 'byte'
        }
        return type_mapping.get(xml_type.lower(), 'string')

    def _is_dropdown_field(self, param_name):
        """Identify if a parameter should be a dropdown field"""
        dropdown_indicators = [
            'account', 'code', 'type', 'category', 'status',
            'source', 'item', 'vote', 'dimension', 'gl', 'vendor',
            'customer', 'employee', 'department'
        ]
        param_lower = param_name.lower()
        return any(indicator in param_lower for indicator in dropdown_indicators)