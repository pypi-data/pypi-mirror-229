"""
Icon
====

Icons are symbols that represent objects and concepts visually. They help users
understand the message without text and should be as informative as possible.
They shouldn't be used to "decorate" the interface. They communicate messages in
the simplest way.
"""
from .base import COLORS, Node

class Icon(Node):
    """Icon component
    """
    NODE_PROPS = ('color', 'size')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'span'
    "Rendered HTML tag."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."
    POSSIBLE_SIZES = ('sm', 'lg', 'xl', 'xxl')
    "Possible values for size argument."

    # Parent Tags can set the arguments of their children Tags, in effect
    # changing their appearance.
    CATCH_PROPS = ('icon_kwargs',)

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-icon-material--{size}')

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-icon-material--{color}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} aria-hidden="true" class="material-icons nj-icon-material {class}"
    {props}>
  {label}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'Icon': Icon,
}
