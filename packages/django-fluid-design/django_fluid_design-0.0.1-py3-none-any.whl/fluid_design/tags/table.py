"""
Table
=====

See: https://www.engie.design/fluid-design-system/components/table/

Data table is used to display and organise all the data set. A data table is
used to compare and analyze data sets.The data informations are always
displayed in row and column.
"""
from .base import Node

class Table(Node):
    """Table component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('style',)
    "Extended Template Tag arguments."
    POSSIBLE_STYLES = ('default', 'striped', 'hover')
    "Possible values for style argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        style = self.eval(self.kwargs.get('style'), context)
        if style in self.POSSIBLE_STYLES[1:]:
            values['class'].append(f'nj-table--{style}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<table class="nj-table {class}" {props}>
  {tmpl_label}
  {child}
</table>
"""
        return self.format(template, values, context)


    def render_tmpl_label(self, values, context):
        """Dynamically render a part of the component's template
        """
        if values['label']:
            return self.format('<caption>{label}</caption>', values)
        return ''


components = {
    'Table': Table,
}
