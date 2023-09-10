"""
Tabs
====

See: https://www.engie.design/fluid-design-system/components/tabs/

Tabs organise content across different screens with a simple navigation.
"""
from django.utils.translation import gettext as _
from .base import Node

class Tabs(Node):
    """Tabs component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('buttons',)
    "Named children."
    NODE_PROPS = ('style',)
    "Extended Template Tag arguments."
    POSSIBLE_STYLES = ('compact', 'spacious', 'stretched')
    "Possible values for style argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['txt_buttons'] = _("Tab system label")

        style = self.eval(self.kwargs.get('style'), context)
        if style in self.POSSIBLE_STYLES:
            values['class'].append(f'nj-tab--{style}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-tab {class}" {props}>
  <div class="nj-tab__items" role="tablist" aria-label="{txt_buttons}">
    {slot_buttons}
  </div>
  <div style="padding-top: var(--nj-size-space-16);">
    {child}
  </div>
</{astag}>
"""
        return self.format(template, values, context)


class TabsButton(Node):
    """Tabs button component
    """
    NODE_PROPS = ('active', 'target_id')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'button'
    "Rendered HTML tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        target = self.eval(self.kwargs.get('target_id'), context)
        if target:
            values['props'].append(('aria-controls', target))

        if self.eval(self.kwargs.get('active'), context):
            values['class'].append('nj-tab__item--active')
            values['props'].append(('aria-selected', 'true'))
            values['props'].append(('tabindex', '0'))
        else:
            values['props'].append(('aria-selected', 'false'))
            values['props'].append(('tabindex', '-1'))

        if self.eval(self.kwargs.get('disabled'), context):
            values['props'].append(('disabled', True))


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-tab__item {class}" role="tab" {props}>
  {label}
</{astag}>
"""
        return self.format(template, values, context)


class TabsPanel(Node):
    """Tabs panel component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('active', 'trigger_id')
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        trigger = self.eval(self.kwargs.get('trigger_id'), context)
        if trigger:
            values['props'].append(('aria-labelledby', trigger))

        if self.eval(self.kwargs.get('active'), context):
            values['class'].append('nj-tab__content--active')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-tab__content {class}" role="tabpanel" tabindex="0" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'Tab': Tabs,
    'T_Btn': TabsButton,
    'T_Panel': TabsPanel,
}
