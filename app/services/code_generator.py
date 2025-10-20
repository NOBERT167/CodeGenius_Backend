from jinja2 import Environment, FileSystemLoader
import os


class CodeGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader("templates"))

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