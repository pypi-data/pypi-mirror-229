"""
Badge
=====

See: https://www.engie.design/fluid-design-system/components/badge/

A badge should be used to bring a meaningful piece of information out. It may
either be textual or numerical. A badge may represent a status or a number of
unread notifications for example. Contrary to tags, badges cannot be
interactive. And multiple badges are not to be used side by side. A number of
variations are suggested here to help you use accessible badges.
"""
from .base import Node

class Badge(Node):
    """Badge component
    """
    NODE_PROPS = ('variant', 'style', 'uppercase', 'size')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'p'
    "Rendered HTML tag."
    POSSIBLE_VARIANTS = ('subtle', 'minimal')
    "Possible values for variant argument."
    POSSIBLE_STYLES = ('danger', 'warning', 'success', 'information',
            'discovery')
    "Possible values for style argument."
    POSSIBLE_SIZES = ('xs', 'sm', 'lg')
    "Possible values for size argument."

    # Parent Tags can set the arguments of their children Tags, in effect
    # changing their appearance.
    CATCH_PROPS = ('badge_kwargs',)

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if self.eval(self.kwargs.get('uppercase'), context):
            values['class'].append('nj-badge--uppercase')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-badge--{size}')

        variant = self.eval(self.kwargs.get('variant'), context)
        if variant in self.POSSIBLE_VARIANTS:
            values['class'].append(f'nj-badge--{variant}')

        style = self.eval(self.kwargs.get('style'), context)
        if style in self.POSSIBLE_STYLES:
            values['class'].append(f'nj-badge--{style}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-badge {class}" {props}>
  {label}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'Badge': Badge,
}
