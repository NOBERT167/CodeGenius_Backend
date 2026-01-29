from jinja2 import Environment, FileSystemLoader
import os
from typing import Optional


class CodeGeneratorWithFilters:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        templates_path = os.path.join(base_dir, "..", "templates")
        templates_path = os.path.normpath(templates_path)
        self.env = Environment(loader=FileSystemLoader(templates_path))

    def generate_full_code(self, parser, page_name, entity_name, filters_config=None):
        """Generate complete MVC code structure with optional filters"""
        try:
            # Determine if filters are enabled
            filters_enabled = filters_config and filters_config.get('enabled', False)

            # Extract filter configurations
            date_filter = None
            status_filter = None
            custom_filters = []

            if filters_enabled:
                if filters_config.get('date_range_filter'):
                    date_filter = filters_config['date_range_filter']

                if filters_config.get('approval_status_filter'):
                    status_filter = filters_config['approval_status_filter']

                custom_filters = filters_config.get('custom_filters', [])

            context = {
                'page_name': page_name,
                'entity_name': entity_name,
                'model_name': f"{page_name}Model",
                'controller_name': f"{page_name}Controller",
                'properties': parser.properties,
                'document_info': parser.document_info,
                'primary_key': parser.document_info.get('primary_key'),
                'user_filter_fields': parser.document_info.get('user_filter_fields', []),
                'datatable_properties': parser.document_info.get('datatable_properties', []),
                # Filter-related context
                'filters_enabled': filters_enabled,
                'date_filter': date_filter,
                'status_filter': status_filter,
                'custom_filters': custom_filters
            }

            return {
                'model': self._generate_model(context),
                'controller': self._generate_controller(context),
                'main_view': self._generate_main_view(context),
                'list_view': self._generate_list_view(context) if not filters_enabled else None,
                'document_view': self._generate_document_view(context)
            }
        except Exception as e:
            raise Exception(f"Error generating full code: {str(e)}")

    def generate_lines_code(self, parser, page_name, entity_name, parent_entity):
        """Generate only lines code"""
        try:
            non_primary_properties = [prop for prop in parser.properties if not prop.get('is_primary_key')]

            context = {
                'page_name': page_name,
                'entity_name': entity_name,
                'parent_entity': parent_entity,
                'model_name': f"{page_name}LinesModel",
                'properties': non_primary_properties,
                'non_primary_count': len(non_primary_properties)
            }

            return {
                'model': self._generate_lines_model({
                    'page_name': page_name,
                    'entity_name': entity_name,
                    'model_name': f"{page_name}LinesModel",
                    'properties': parser.properties
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
            # Use different template based on filter configuration
            if context.get('filters_enabled'):
                template = self.env.get_template('controller_with_filters_template.j2')
            else:
                template = self.env.get_template('controller_template.j2')
            return template.render(**context)
        except Exception as e:
            return f"// Error generating controller: {str(e)}"

    def _generate_main_view(self, context):
        try:
            # Use different template based on filter configuration
            if context.get('filters_enabled'):
                template = self.env.get_template('main_view_with_filters_template.j2')
            else:
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

    # Function generation methods (unchanged)
    def generate_function_header_code(self, xml_string, page_name, function_name):
        """Generate code for header function"""
        try:
            from .function_parser import FunctionParser
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
        """Generate code for line function"""
        try:
            from .function_parser import FunctionParser
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
        """Check if function has docNo parameter"""
        docno_indicators = ['docno', 'documentno', 'no', 'code']
        return any(param['name'].lower() in docno_indicators for param in parameters)

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