"""
Grid
====

See: https://www.engie.design/fluid-design-system/components/grid/

All about the grid! Grid systems are used to create perfect layouts. Our grid
system is based on the Bootstrap v4 grid. Use the mobile-first flexbox grid to
build layouts of all shapes and sizes with a twelve column system, five default
responsive tiers, Sass variables and mixins, and dozens of predefined classes.
"""
from .base import Node

class Grid(Node):
    """Grid component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    DEFAULT_TAG = 'div'
    "Rendered HTML tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="container {class}" {props}>{child}</{astag}>
"""
        return self.format(template, values)


class GridRow(Node):
    """Grid row component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    COL_SIZES = ('col', 'sm', 'md', 'lg')
    "Column sizes."
    NODE_PROPS = (
            'gutter',
            *['align_%s' % x for x in COL_SIZES],
            *['valign_%s' % x for x in COL_SIZES])
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'div'
    "Rendered HTML tag."
    POSSIBLE_ALIGNS = ('start', 'center', 'end', 'around', 'between')
    "Possible values for align argument."
    POSSIBLE_VALIGNS = ('start', 'center', 'end')
    "Possible values for valign argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        for size in self.COL_SIZES:
            align = self.eval(self.kwargs.get('align_%s' % size), context)

            if size == 'col':
                prefix = 'justify-content'
            else:
                prefix = f'justify-content-{size}'

            if align in self.POSSIBLE_ALIGNS:
                values['class'].append(f'{prefix}-{align}')

            valign = self.eval(self.kwargs.get('valign_%s' % size), context)

            if size == 'col':
                prefix = 'align-items'
            else:
                prefix = f'align-items-{size}'

            if valign in self.POSSIBLE_VALIGNS:
                values['class'].append(f'{prefix}-{valign}')

        if not self.eval(self.kwargs.get('gutter', True), context):
            values['class'].append('no-gutters')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = '<{astag} class="row {class}" {props}>{child}</{astag}>'
        return self.format(template, values)


class GridColumn(Node):
    """Grid column component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    COL_SIZES = ('col', 'sm', 'md', 'lg', 'xl')
    "Column sizes."
    NODE_PROPS = (
            'order',
            *COL_SIZES,
            *['offset_%s' % x for x in COL_SIZES],
            *['ml_%s' % x for x in COL_SIZES],
            *['mr_%s' % x for x in COL_SIZES])
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'div'
    "Rendered HTML tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        for size in self.COL_SIZES:
            width = self.eval(self.kwargs.get(size), context)
            try:
                if width not in ('fill', 'shrink'):
                    width = int(width)
            except (ValueError, TypeError):
                width = None

            if size == 'col':
                prefix = 'col'
            else:
                prefix = f'col-{size}'

            if width == 'fill':
                values['class'].append(prefix)
            elif width == 'shrink':
                values['class'].append(f'{prefix}-auto')
            elif width:
                values['class'].append(f'{prefix}-{width}')

            offset = self.eval(self.kwargs.get(f'offset_{size}'), context)
            try:
                offset = int(offset)
            except (ValueError, TypeError):
                offset = None

            if offset:
                if size == 'col':
                    prefix = 'offset'
                else:
                    prefix = f'offset-{size}'

                values['class'].append(f'{prefix}-{offset}')

            margin_left = self.eval(self.kwargs.get(f'ml_{size}'), context)
            try:
                if margin_left not in ('auto',):
                    margin_left = int(margin_left)
            except (ValueError, TypeError):
                margin_left = None

            if margin_left:
                if size == 'col':
                    prefix = 'ml'
                else:
                    prefix = f'ml-{size}'

                values['class'].append(f'{prefix}-{margin_left}')

            margin_right = self.eval(self.kwargs.get(f'mr_{size}'), context)
            try:
                if margin_right not in ('auto',):
                    margin_right = int(margin_right)
            except (ValueError, TypeError):
                margin_right = None

            if margin_right:
                if size == 'col':
                    prefix = 'mr'
                else:
                    prefix = f'mr-{size}'

                values['class'].append(f'{prefix}-{margin_right}')

        order = self.eval(self.kwargs.get('order'), context)
        try:
            order = int(order)
            values['class'].append(f'order-{order}')
        except (ValueError, TypeError):
            pass


    def render_default(self, values, context):
        """Html output of the component
        """
        template = '<{astag} class="{class}" {props}>{child}</{astag}>'
        return self.format(template, values)


components = {
    'Grid': Grid,
    'Row': GridRow,
    'Col': GridColumn,
}
