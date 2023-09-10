"""
Floating Action Button
======================

See: https://www.engie.design/fluid-design-system/components/fab/

Floating Action Buttons are just like buttons but they are not static. They
follow the journey of the user and display contextual actions at the perfect
moment. They are useful for mobile navigation. 
"""

from .base import Node

class Fab(Node):
    """Floating action button component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('menu',)
    "Named children."
    NODE_PROPS = ('disabled', 'size', 'placement')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('list', 'wrapper')
    "Prepare xxx_class and xxx_props values."
    POSSIBLE_SIZES = ('sm',)
    "Possible values for size argument."
    POSSIBLE_PLACEMENTS = ('right',)
    "Possible values for placement argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-fab--{size}')
            values['list_class'].append(f'nj-fab__actions--{size}')
        placement = self.eval(self.kwargs.get('placement'), context)
        if placement in self.POSSIBLE_PLACEMENTS:
            values['wrapper_props'].append(('data-placement', placement))

        if self.eval(self.kwargs.get('disabled'), context):
            values['class'].append('disabled')
            values['props'].append(('disabled', ''))


    def render_default(self, values, context):
        """Html output of the component
        """
        if 'menu' in self.slots:
            template = """
<div class="nj-fab-menu {wrapper_class}" {wrapper_props}>
  <button type="button" class="nj-fab {class}" {props}>
    {child}
  </button>
  <ul class="nj-fab__actions {list_class}" {list_props}>
    {slot_menu}
  </ul>
</div>
"""
        else:
            template = """
<button type="button" class="nj-fab {class}" {props}>
  {child}
</button>
"""
        return self.format(template, values, context)


class FabItem(Node):
    """Floating action menu component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-fab__item">
  <button type="button" class="nj-fab nj-fab--light nj-fab--sm {class}" {props}>
    {child}
  </button>
</li>
"""
        return self.format(template, values, context)


components = {
    'Fab': Fab,
    'FabItem': FabItem,
}
