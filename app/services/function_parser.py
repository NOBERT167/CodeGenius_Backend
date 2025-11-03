import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Any


class FunctionParser:
    def __init__(self, xml_string: str):
        self.xml_string = xml_string
        self.parameters = []

    def parse(self):
        """Parse XML string and extract function parameters"""
        try:
            # Clean the XML string - remove namespaces if present
            clean_xml = self._clean_xml(self.xml_string)

            # Parse XML
            root = ET.fromstring(clean_xml)

            # Find the sequence element
            sequence = root.find('.//sequence')
            if sequence is not None:
                for element in sequence.findall('element'):
                    param = self._parse_parameter_element(element)
                    if param:
                        self.parameters.append(param)

            return self
        except Exception as e:
            raise Exception(f"Error parsing function XML: {str(e)}")

    def _clean_xml(self, xml_string: str) -> str:
        """Remove XML namespaces and clean up the string"""
        # Remove xmlns declarations
        clean_xml = re.sub(r'xmlns[^=]*="[^"]*"', '', xml_string)
        # Remove any other namespaces
        clean_xml = re.sub(r'<(\w+):(\w+)', r'<\2', clean_xml)
        clean_xml = re.sub(r'</(\w+):(\w+)', r'</\2', clean_xml)
        return clean_xml.strip()

    def _parse_parameter_element(self, element) -> Dict[str, Any]:
        """Parse individual parameter element"""
        try:
            param_name = element.get('name', '')
            param_type = element.get('type', 'string')
            min_occurs = element.get('minOccurs', '1')
            max_occurs = element.get('maxOccurs', '1')

            if not param_name:
                return None

            return {
                'name': param_name,
                'type': param_type,
                'min_occurs': min_occurs,
                'max_occurs': max_occurs,
                'is_required': min_occurs == '1',
                'is_array': max_occurs != '1'
            }
        except Exception as e:
            print(f"Error parsing parameter element: {e}")
            return None

    def get_parameters(self) -> List[Dict]:
        """Get parsed parameters with enhanced information"""
        enhanced_params = []

        for param in self.parameters:
            enhanced_param = {
                'name': param['name'],
                'original_name': param['name'],
                'csharp_name': self._normalize_parameter_name(param['name']),
                'display_name': self._format_display_name(param['name']),
                'type': self._map_xml_type_to_csharp(param['type']),
                'xml_type': param['type'],
                'is_required': param['is_required'],
                'is_array': param['is_array'],
                'is_dropdown': self._is_dropdown_field(param['name']),
                'is_date': self._is_date_field(param['name'], param['type']),
                'is_amount': self._is_amount_field(param['name']),
                'description': self._generate_description(param['name'], param['type'])
            }
            enhanced_params.append(enhanced_param)

        return enhanced_params

    def _normalize_parameter_name(self, name: str) -> str:
        """Normalize parameter name to C# property convention"""
        # Handle camelCase, snake_case, and kebab-case
        clean_name = re.sub(r'[^a-zA-Z0-9]', ' ', name)
        return ''.join(word.capitalize() for word in clean_name.split())

    def _format_display_name(self, name: str) -> str:
        """Format parameter name for display"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', ' ', name)
        return ' '.join(word.capitalize() for word in clean_name.split())

    def _map_xml_type_to_csharp(self, xml_type: str) -> str:
        """Map XML schema types to C# types"""
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

    def _is_dropdown_field(self, param_name: str) -> bool:
        """Identify if a parameter should be a dropdown field"""
        dropdown_indicators = [
            'account', 'code', 'type', 'category', 'status',
            'source', 'item', 'vote', 'dimension', 'gl', 'vendor',
            'customer', 'employee', 'department', 'county', 'subcounty',
            'requestsource'
        ]
        param_lower = param_name.lower()
        return any(indicator in param_lower for indicator in dropdown_indicators)

    def _is_date_field(self, param_name: str, xml_type: str) -> bool:
        """Check if field is a date field"""
        date_indicators = ['date', 'time', 'created', 'modified', 'start', 'end']
        return (xml_type.lower() in ['date', 'datetime'] or
                any(indicator in param_name.lower() for indicator in date_indicators))

    def _is_amount_field(self, param_name: str) -> bool:
        """Check if field is an amount field"""
        amount_indicators = ['amount', 'total', 'cost', 'price', 'value', 'sum', 'balance']
        return any(indicator in param_name.lower() for indicator in amount_indicators)

    def _generate_description(self, param_name: str, xml_type: str) -> str:
        """Generate description for parameter"""
        if self._is_date_field(param_name, xml_type):
            return "Date field"
        elif self._is_amount_field(param_name):
            return "Amount field"
        elif self._is_dropdown_field(param_name):
            return "Selection field"
        elif xml_type == 'boolean':
            return "Boolean indicator"
        return "Input field"