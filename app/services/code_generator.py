from jinja2 import Environment, FileSystemLoader
import os


class CodeGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader("templates"))

    def generate_full_code(self, parser, page_name, entity_name):
        """Generate complete MVC code structure"""
        context = {
            'page_name': page_name,
            'entity_name': entity_name,
            'model_name': f"{page_name}Model",
            'controller_name': f"{page_name}Controller",
            'properties': parser.properties,
            'document_info': parser.document_info,
            'primary_key': parser.document_info['primary_key'],
            'user_filter_fields': parser.document_info['user_filter_fields'],
            'datatable_properties': parser.document_info['datatable_properties']
        }

        return {
            'model': self._generate_model(context),
            'controller': self._generate_controller(context),
            'main_view': self._generate_main_view(context),
            'list_view': self._generate_list_view(context),
            'document_view': self._generate_document_view(context)
        }

    def generate_lines_code(self, parser, page_name, entity_name, parent_entity):
        """Generate only lines code"""
        context = {
            'page_name': page_name,
            'entity_name': entity_name,
            'parent_entity': parent_entity,
            'model_name': f"{page_name}LinesModel",
            'properties': parser.properties
        }

        return {
            'model': self._generate_lines_model(context),
            'partial_view': self._generate_lines_view(context),
            'controller_method': self._generate_lines_controller_method(context)
        }

    def _generate_model(self, context):
        template = self.env.get_template('model_template.j2')
        return template.render(**context)

    def _generate_controller(self, context):
        template = self.env.get_template('controller_template.j2')
        return template.render(**context)

    def _generate_main_view(self, context):
        template = self.env.get_template('main_view_template.j2')
        return template.render(**context)

    def _generate_list_view(self, context):
        template = self.env.get_template('list_view_template.j2')
        return template.render(**context)

    def _generate_document_view(self, context):
        template = self.env.get_template('document_view_template.j2')
        return template.render(**context)

    def _generate_lines_model(self, context):
        template = self.env.get_template('lines_model_template.j2')
        return template.render(**context)

    def _generate_lines_view(self, context):
        template = self.env.get_template('lines_view_template.j2')
        return template.render(**context)

    def _generate_lines_controller_method(self, context):
        template = self.env.get_template('lines_controller_method_template.j2')
        return template.render(**context)