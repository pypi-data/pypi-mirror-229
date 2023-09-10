"""
Spinner
=======

See: https://www.engie.design/fluid-design-system/components/spinner/

Spinner allows the user to know when the system is in progress and when he will
end. The spinner is used to indicate the current status of a loading screen or
a loading data.
"""
from django.utils.translation import gettext as _
#-
from .base import COLORS, Node

class Spinner(Node):
    """Spinner component
    """
    NODE_PROPS = ('color', 'size')
    "Extended Template Tag arguments."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."
    POSSIBLE_SIZES = ('sm', 'md', 'xs', 'xxs')
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['txt_loading'] = _("Loading...")

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-spinner--{color}')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-spinner--{size}')


    def render_default(self, values, context):
        """Html output of the component
        """
        if values['astag'] == 'span':
            template = """
<span aria-live="polite" aria-atomic="true" class="nj-spinner {class}" {props}>
  <span class="nj-sr-only">{txt_loading}</span>
  {label}
</span>
"""
        else:
            template = """
<{astag} aria-live="polite" aria-atomic="true" class="nj-spinner {class}" {props}>
  <p class="nj-sr-only">{txt_loading}</p>
  {label}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'Spinner': Spinner,
}
