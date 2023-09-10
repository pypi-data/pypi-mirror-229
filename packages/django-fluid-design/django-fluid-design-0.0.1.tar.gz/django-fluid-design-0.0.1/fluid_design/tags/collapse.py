"""
Collapse
========

See: https://www.engie.design/fluid-design-system/components/collapse/

Collapses allow users to toggle the visibility of a content

How it works
------------

The collapse JavaScript plugin is used to show and hide content. Buttons or
anchors are used as triggers that are mapped to specific elements you toggle.
Collapsing an element will animate the height from its current value to 0.
Given how CSS handles animations, you cannot use padding on a .nj-collapse
element. Instead, use the class as an independent wrapping element.
"""

from .base import Node

class Collapse(Node):
    """Collapse component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-collapse {class}" {props}>
  <div class="nj-card nj-card__body">
    {child}
  </div>
</{astag}>
"""
        return self.format(template, values, context)


class CollapseButton(Node):
    """Collapse button component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    MODES = ('default', 'anchor')
    "Available variants."
    NODE_PROPS = ('target', 'controls')
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        target = self.eval(self.kwargs.get('target'), context)
        controls = self.eval(self.kwargs.get('controls'), context)

        values['target'] = target
        if controls:
            values['controls'] = controls
        elif target and target.startswith('#'):
            values['controls'] = target[1:]
        else:
            values['controls'] = ''


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<button class="nj-btn {class}" type="button" data-toggle="collapse"
    data-target="{target}" aria-expanded="false" aria-controls="{controls}"
    {props}>
  {child}
</button>
"""
        return self.format(template, values, context)


    def render_anchor(self, values, context):
        """Html output of the component
        """
        template = """
<a class="nj-btn" role="button" data-toggle="collapse"
    href="{target}" aria-expanded="false" aria-controls="{controls}" {props}>
  {child}
</a>
"""
        return self.format(template, values, context)


components = {
    'CollapseBtn': CollapseButton,
    'Collapse': Collapse,
}
