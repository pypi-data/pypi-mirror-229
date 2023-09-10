"""
Inline Message
==============

See: https://www.engie.design/fluid-design-system/components/inline-message/
"""
from django.utils.translation import gettext as _
#-
from . base import Node

class InlineMessage(Node):
    """Inline message component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('title',)
    "Named children."
    NODE_PROPS = ('style', 'icon', 'close')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('icon', 'close')
    "Prepare xxx_class and xxx_props values."
    POSSIBLE_STYLES = ('error', 'info', 'success', 'warning', 'fatal-error')
    "Possible values for style argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates.
        """
        values['txt_close'] = _("Hide message")
        style = self.eval(self.kwargs.get('style'), context)
        if style != 'error':
            values['class'].append(f'nj-inline-message--{style}')
        if style == 'fatal-error':
            values['close_class'].append('nj-icon-btn--inverse')
        if style in self.POSSIBLE_STYLES:
            values['icon_class'].append(f'nj-status-indicator--{style}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-inline-message {class}" {props}>
  {tmpl_icon}
  <div class="nj-inline-message__content">
   <h4 class="nj-inline-message__title">{slot_title}</h4>
   <p class="nj-inline-message__body">{child}</p>
  </div>
  {tmpl_close}
</{astag}>
"""
        return self.format(template, values, context)


    def render_tmpl_icon(self, values, context):
        """Dynamically render a part of the component's template.
        """
        show_icon = self.eval(self.kwargs.get('icon', True), context)
        if not show_icon:
            return ''
        style = self.eval(self.kwargs.get('style'), context)
        if style == 'fatal-error':
            return ''
        tmpl = """
<div class="nj-inline-message__status nj-status-indicator {icon_class}"
    aria-hidden="true" {icon_props}>
  <div class="nj-status-indicator__svg"></div>
</div>
"""
        return tmpl.format(**values)


    def render_tmpl_close(self, values, context):
        """Dynamically render a part of the component's template.
        """
        show_close = self.eval(self.kwargs.get('close'), context)
        if not show_close:
            return ''
        tmpl = """
<button class="nj-inline-message__close nj-icon-btn {close_class}"
    {close_props}>
  <span class="nj-sr-only">{txt_close}</span>
  <span aria-hidden="true" class="nj-icon-btn__icon material-icons">close</span>
</button>
"""
        return tmpl.format(**values)


components = {
    'Message': InlineMessage,
}
