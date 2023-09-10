"""
Skeleton
========

See: https://www.engie.design/fluid-design-system/components/skeleton/

Show a preview placeholder of your content to reduce load-time frustration.
"""
from django.utils.translation import gettext as _
#-
from .base import Node

class Skeleton(Node):
    """Skeleton component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if not values['label']:
            values['label'] = _("Loading...")


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-skeleton-container {class}" {props}>
  <span class="nj-sr-only">{label}</span>
  {child}
</div>
"""
        return self.format(template, values, context)


class SkeletonItem(Node):
    """Skeleton component
    """
    NODE_PROPS = ('shape', 'height', 'size')
    "Extended Template Tag arguments."
    POSSIBLE_SHAPES = ('icon', 'svg', 'circle', 'rectangle')
    "Possible values for shape argument."
    POSSIBLE_HEIGHTS = ('peta', 'tera', 'giga', 'mega', 'kilo', 'hecto', 'deca',
            'base', 'deci', 'centi')
    "Possible values for height argument."
    POSSIBLE_SIZES = ('sm', 'base', 'lg', 'xl')
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        shape = self.eval(self.kwargs.get('shape'), context)
        if shape in self.POSSIBLE_SHAPES:
            if shape in ('icon', 'svg'):
                values['class'].append('nj-skeleton--area')
            else:
                values['class'].append(f'nj-skeleton--{shape}')
        values['shape'] = shape

        height = self.eval(self.kwargs.get('height'), context)
        if height in self.POSSIBLE_HEIGHTS:
            values['class'].append(f'nj-skeleton--{height}')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-skeleton--{size}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<div aria-hidden="true" class="nj-skeleton {class}" {props}>
  {tmpl_child}
</div>
"""
        return self.format(template, values, context)


    def render_tmpl_child(self, values, context):
        """Dynamically render a part of the component's template
        """
        if values['shape'] == 'icon':
            return """
<span class="nj-skeleton__icon material-icons nj-icon-material nj-icon-material--tertiary nj-icon-material--xl">
  image
</span>
"""
        if values['shape'] == 'svg':
            return """
<svg class="nj-skeleton__icon" width="48" height="48" viewBox="0 0 36 36"
    fill="none" xmlns="http://www.w3.org/2000/svg">
  <path
    d="M36 32V4C36 1.8 34.2 0 32 0H4C1.8 0 0 1.8 0 4V32C0 34.2 1.8 36 4 36H32C34.2 36 36 34.2 36 32ZM11 21L16 27.02L23 18L32 30H4L11 21Z"
    fill="currentColor" />
</svg>
"""
        return ''


components = {
    'Skeleton': Skeleton,
    'Bone': SkeletonItem,
}
