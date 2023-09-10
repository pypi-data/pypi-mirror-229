"""
Icon Button
===========

See: https://www.engie.design/fluid-design-system/components/icon-button/
"""
from .base import COLORS, Node

class IconButton(Node):
    """IconButton component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon',)
    "Named children."
    NODE_PROPS = ('disabled', 'color', 'size')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'button'
    "Rendered HTML tag."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."
    POSSIBLE_SIZES = ('xs', 'sm', 'lg')
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if self.eval(self.kwargs.get('disabled'), context):
            values['props'].append(('disabled', ''))

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-icon-btn--{color}')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-icon-btn--{size}')


    def render_default(self, values, context):
        """Html output of the component
        """
        if values['child']:
            template = """
<{astag} class="nj-icon-btn {class}" {props}>
  <span class="nj-sr-only">{child}</span>
  {slot_icon}
</{astag}>
"""
        else:
            template = """
<{astag} class="nj-icon-btn {class}" {props}>
  {slot_icon}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'IconButton': IconButton,
}
