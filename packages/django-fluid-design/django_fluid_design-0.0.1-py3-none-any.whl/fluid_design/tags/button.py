"""
Button
======

See: https://www.engie.design/fluid-design-system/components/button/

Buttons allow users to interact with the product and trigger actions. They can
be of different sizes, colors and status.
In terms of accessibility, be mindful of people using assistive technologies:
don’t use links instead of buttons to trigger actions.
"""

from .base import COLORS, Node

class Button(Node):
    """Button component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon',)
    "Named children."
    NODE_PROPS = ('disabled', 'variant', 'color', 'size')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'button'
    "Rendered HTML tag."
    POSSIBLE_VARIANTS = ('subtle', 'minimal')
    "Possible values for variant argument."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."
    POSSIBLE_SIZES = ('xs', 'sm', 'lg')
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if self.eval(self.kwargs.get('disabled'), context):
            values['props'].append(('disabled', ''))

        variant = self.eval(self.kwargs.get('variant'), context)
        if variant in self.POSSIBLE_VARIANTS:
            values['class'].append(f'nj-btn--{variant}')

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-btn--{color}')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-btn--{size}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-btn {class}" {props}>
  {slot_icon}
  {child}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'Button': Button,
}
