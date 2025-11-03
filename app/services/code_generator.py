from jinja2 import Environment, FileSystemLoader
import os
# from function_parser import FunctionParser
from .function_parser import FunctionParser


class CodeGenerator:
    def __init__(self):
        # self.env = Environment(loader=FileSystemLoader("templates"))
        # Get the directory where this file lives (app/services/)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Move up one level (to app/) and join 'templates'
        templates_path = os.path.join(base_dir, "..", "templates")

        # Normalize the path for Windows
        templates_path = os.path.normpath(templates_path)

        self.env = Environment(loader=FileSystemLoader(templates_path))
    def generate_full_code(self, parser, page_name, entity_name):
        """Generate complete MVC code structure"""
        try:
            context = {
                'page_name': page_name,
                'entity_name': entity_name,
                'model_name': f"{page_name}Model",
                'controller_name': f"{page_name}Controller",
                'properties': parser.properties,
                'document_info': parser.document_info,
                'primary_key': parser.document_info.get('primary_key'),
                'user_filter_fields': parser.document_info.get('user_filter_fields', []),
                'datatable_properties': parser.document_info.get('datatable_properties', [])
            }

            return {
                'model': self._generate_model(context),
                'controller': self._generate_controller(context),
                'main_view': self._generate_main_view(context),
                'list_view': self._generate_list_view(context),
                'document_view': self._generate_document_view(context)
            }
        except Exception as e:
            raise Exception(f"Error generating full code: {str(e)}")

    def generate_lines_code(self, parser, page_name, entity_name, parent_entity):
        """Generate only lines code"""
        try:
            # Filter out primary key properties for the view
            non_primary_properties = [prop for prop in parser.properties if not prop.get('is_primary_key')]

            context = {
                'page_name': page_name,
                'entity_name': entity_name,
                'parent_entity': parent_entity,
                'model_name': f"{page_name}LinesModel",
                'properties': non_primary_properties,  # Use filtered properties
                'non_primary_count': len(non_primary_properties)
            }

            return {
                'model': self._generate_lines_model({
                    'page_name': page_name,
                    'entity_name': entity_name,
                    'model_name': f"{page_name}LinesModel",
                    'properties': parser.properties  # Keep all properties for model
                }),
                'partial_view': self._generate_lines_view(context),
                'controller_method': self._generate_lines_controller_method({
                    'page_name': page_name,
                    'entity_name': entity_name,
                    'model_name': f"{page_name}LinesModel",
                    'properties': parser.properties
                })
            }
        except Exception as e:
            raise Exception(f"Error generating lines code: {str(e)}")

    def _generate_model(self, context):
        try:
            template = self.env.get_template('model_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating model: {str(e)}"

    def _generate_controller(self, context):
        try:
            template = self.env.get_template('controller_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating controller: {str(e)}"

    def _generate_main_view(self, context):
        try:
            template = self.env.get_template('main_view_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"<!-- Error generating main view: {str(e)} -->"

    def _generate_list_view(self, context):
        try:
            template = self.env.get_template('list_view_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"<!-- Error generating list view: {str(e)} -->"

    def _generate_document_view(self, context):
        try:
            template = self.env.get_template('document_view_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"<!-- Error generating document view: {str(e)} -->"

    def _generate_lines_model(self, context):
        try:
            template = self.env.get_template('lines_model_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating lines model: {str(e)}"

    def _generate_lines_view(self, context):
        try:
            template = self.env.get_template('lines_view_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"<!-- Error generating lines view: {str(e)} -->"

    def _generate_lines_controller_method(self, context):
        try:
            template = self.env.get_template('lines_controller_method_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating lines controller method: {str(e)}"

    # Add this import at the top
    from services.function_parser import FunctionParser

    # Update the function generation methods
    def generate_function_header_code(self, xml_string, page_name, function_name):
        """Generate code for header function (without docNo parameter)"""
        try:
            # Parse XML string
            parser = FunctionParser(xml_string).parse()
            parameters = parser.get_parameters()

            context = {
                'page_name': page_name,
                'function_name': function_name,
                'model_name': f"{page_name}ViewModel",
                'parameters': parameters,
                'has_docno_param': self._has_docno_parameter(parameters)
            }

            return {
                'model': self._generate_function_model(context),
                'controller': self._generate_function_controller(context),
                'view': self._generate_function_view(context),
                'javascript': self._generate_function_javascript(context)
            }
        except Exception as e:
            raise Exception(f"Error generating function header code: {str(e)}")

    def generate_function_line_code(self, xml_string, page_name, function_name, parent_entity):
        """Generate code for line function (with docNo parameter)"""
        try:
            # Parse XML string
            parser = FunctionParser(xml_string).parse()
            parameters = parser.get_parameters()

            context = {
                'page_name': page_name,
                'function_name': function_name,
                'parent_entity': parent_entity,
                'model_name': f"{page_name}LinesViewModel",
                'parameters': parameters,
                'has_docno_param': self._has_docno_parameter(parameters)
            }

            return {
                'model': self._generate_lines_function_model(context),
                'controller_methods': self._generate_lines_function_controller(context),
                'partial_view': self._generate_lines_function_view(context),
                'javascript': self._generate_lines_function_javascript(context)
            }
        except Exception as e:
            raise Exception(f"Error generating function line code: {str(e)}")

    def _has_docno_parameter(self, parameters):
        """Check if function has docNo parameter (indicates line function)"""
        docno_indicators = ['docno', 'documentno', 'no', 'code']
        return any(param['name'].lower() in docno_indicators for param in parameters)

    def _parse_function_parameters(self, function_definition):
        """Parse SOAP function parameters from XML definition"""
        parameters = []

        try:
            # Extract parameters from the complexType sequence
            sequence = function_definition.get('complexType', {}).get('sequence', {})
            elements = sequence.get('element', [])

            if not isinstance(elements, list):
                elements = [elements]

            for element in elements:
                param_name = element.get('@name', '')
                param_type = element.get('@type', 'string')

                # Map XML types to C# types
                csharp_type = self._map_xml_type_to_csharp(param_type)

                parameters.append({
                    'name': param_name,
                    'csharp_name': self._normalize_parameter_name(param_name),
                    'display_name': self._format_display_name(param_name),
                    'type': csharp_type,
                    'xml_type': param_type,
                    'is_required': element.get('@minOccurs', '1') == '1'
                })

        except Exception as e:
            print(f"Error parsing function parameters: {e}")

        return parameters

    def _map_xml_type_to_csharp(self, xml_type):
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
            'float': 'float'
        }
        return type_mapping.get(xml_type, 'string')

    def _normalize_parameter_name(self, name):
        """Normalize parameter name to C# property naming convention"""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _format_display_name(self, name):
        """Format parameter name for display"""
        return ' '.join(word.capitalize() for word in name.split('_'))

    def _has_docno_parameter(self, parameters):
        """Check if function has docNo parameter (indicates line function)"""
        docno_indicators = ['docno', 'documentno', 'no', 'code']
        return any(param['name'].lower() in docno_indicators for param in parameters)

    # Template generation methods for functions
    def _generate_function_model(self, context):
        try:
            template = self.env.get_template('function_model_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating function model: {str(e)}"

    def _generate_function_controller(self, context):
        try:
            template = self.env.get_template('function_controller_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating function controller: {str(e)}"

    def _generate_function_view(self, context):
        try:
            template = self.env.get_template('function_view_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"<!-- Error generating function view: {str(e)} -->"

    def _generate_function_javascript(self, context):
        try:
            template = self.env.get_template('function_javascript_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating function javascript: {str(e)}"

    def _generate_lines_function_model(self, context):
        try:
            template = self.env.get_template('lines_function_model_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating lines function model: {str(e)}"

    def _generate_lines_function_controller(self, context):
        try:
            template = self.env.get_template('lines_function_controller_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating lines function controller: {str(e)}"

    def _generate_lines_function_view(self, context):
        try:
            template = self.env.get_template('lines_function_view_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"<!-- Error generating lines function view: {str(e)} -->"

    def _generate_lines_function_javascript(self, context):
        try:
            template = self.env.get_template('lines_function_javascript_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating lines function javascript: {str(e)}"