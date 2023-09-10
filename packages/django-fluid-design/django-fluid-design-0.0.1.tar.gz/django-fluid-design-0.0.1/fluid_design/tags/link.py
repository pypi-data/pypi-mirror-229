"""
Link
====

See: https://www.engie.design/fluid-design-system/components/link/

Links are key elements for navigation. They should only be used for this
purpose, and not to trigger specific actions. For the latter case, use a button
instead. Different colors from our design system can be used to highlight
different categories of links.
To improve accessibility, we recommend to always use underscoring so that links
can easily be spotted by users. 
""" # pylint:disable=line-too-long

from .base import Node

class Link(Node):
    """Link component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon',)
    "Named children."
    NODE_PROPS = ('icon_before', 'size', 'style', 'external')
    "Extended Template Tag arguments."
    POSSIBLE_SIZES = ('sm',)
    "Possible values for size argument."
    POSSIBLE_STYLES = ('bold', 'contextual', 'grayed', 'high-contrast',
            'inverse')
    "Possible values for style argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        style = self.eval(self.kwargs.get('style'), context)
        if style in self.POSSIBLE_STYLES:
            values['class'].append(f'nj-link--{style}')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-link--{size}')

        if 'icon' in self.slots:
            values['class'].append('nj-link-icon')


    def render_default(self, values, context):
        """Html output of the component
        """
        if self.eval(self.kwargs.get('external'), context):
            template = """
<a target="_blank" class="nj-link nj-link-icon {class}" {props}>
  {child}
  <span class="nj-sr-only">&nbsp;(open in new tab)</span>
  <span aria-hidden="true" class="material-icons">open_in_new</span>
</a>
"""
        elif 'icon' in self.slots:
            if self.eval(self.kwargs.get('icon_before'), context):
                template = """
<a class="nj-link nj-link-icon--before {class}" {props}>
  {slot_icon}
  {child}
</a>
"""
            else:
                template = """
<a class="nj-link {class}" {props}>
  {child}
  {slot_icon}
</a>
"""
        else:
            template = """
<a class="nj-link {class}" {props}>
  {child}
</a>
"""
        return self.format(template, values, context)


components = {
    'Link': Link,
}
