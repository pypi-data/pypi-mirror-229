"""
List
====

See: https://www.engie.design/fluid-design-system/components/list/

Lists are a flexible and powerful component for displaying a series of content.
"""
from .base import Node

class List(Node):
    """List component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('size', 'border', 'spaced')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'ul'
    "Rendered HTML tag."
    POSSIBLE_SIZES = ('sm',)
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if not self.eval(self.kwargs.get('border', True), context):
            values['class'].append('nj-list-group--no-border')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-list-group--{size}')

        if self.eval(self.kwargs.get('spaced'), context):
            values['class'].append('nj-list-group--spaced-items')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-list-group {class}" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values, context)


class ListItem(Node):
    """List component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon_first', 'icon_last')
    "Named children."
    NODE_PROPS = ('active', 'border', 'click', 'disabled')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'span'
    "Rendered HTML tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        context['icon_kwargs'] = {
            'class': 'nj-list-group__item-icon',
        }
        context['icon_last_icon_kwargs'] = {
            'class': 'nj-list-group__item-right-content',
        }
        context['icon_last_badge_kwargs'] = {
            'class': 'nj-list-group__item-right-content',
        }
        context['icon_last_tag_kwargs'] = {
            'class': 'nj-list-group__item-right-content',
        }

        if self.eval(self.kwargs.get('click'), context):
            values['class'].append('nj-list-group__item--clickable')

        if self.eval(self.kwargs.get('border'), context):
            values['class'].append('nj-list-group__item--right-border')

        if self.eval(self.kwargs.get('active'), context):
            values['class'].append('active')
            values['props'].append(('aria-current', 'true'))

        if self.eval(self.kwargs.get('disabled'), context):
            values['class'].append('disabled')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-list-group__item {class}" {props}>
  {slot_icon_first}
  {tmpl_content}
  {slot_icon_last}
</li>
"""
        return self.format(template, values, context)


    def render_tmpl_content(self, values, context):
        """Dynamically render a part of the component's template
        """
        if 'icon_last' in self.slots:
            tmpl = """
<{astag} class="nj-list-group__item-content">
  {child}
</{astag}>
"""
            return self.format(tmpl, values)
        return values['child']


components = {
    'List': List,
    'Li': ListItem,
}
