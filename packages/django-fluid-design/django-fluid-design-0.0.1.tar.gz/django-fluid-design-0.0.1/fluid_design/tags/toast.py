"""
Toast
=====

See: https://www.engie.design/fluid-design-system/components/toast/

Toasts are non-modal dialogs used as a way to provide feedback following user
action. They are typically composed of a short message appearing at the bottom
of the screen, to make them as discreet as possible.
"""
from django.utils.translation import gettext as _
#-
from .base import COLORS, Node

class Toast(Node):
    """Toast component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon',)
    "Named children."
    NODE_PROPS = ('content_id', 'color', 'btncolor', 'gauge')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('button', 'gauge')
    "Prepare xxx_class and xxx_props values."
    POSSIBLE_COLORS = COLORS
    "Possible values for color or btncolor argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        context['icon_icon_kwargs'] = {
            'class': 'nj-toast__icon',
        }

        values['txt_close'] = _("Close notification")
        values['txt_gauge'] = _("The toast will be automatically closed in "
                "%(gauge)ss")

        values['content_id'] = self.eval(self.kwargs.get('content_id'), context)

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-toast--{color}')

        color = self.eval(self.kwargs.get('btncolor'), context)
        if color in self.POSSIBLE_COLORS:
            values['button_class'].append(f'nj-icon-btn--{color}')

        values['gauge'] = gauge = self.eval(self.kwargs.get('gauge'), context)
        if gauge:
            values['txt_gauge'] = values['txt_gauge'] % {'gauge': gauge}
            if gauge != 5:
                values['gauge_props'].append(
                        ('style', f'animation-duration: {gauge}s;'))


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-toast {class}" {props}>
  <div class="nj-toast__body">
    {slot_icon}
    <div class="nj-toast__content">
      {child}
    </div>
  </div>
  {tmpl_closebtn}
  {tmpl_gauge}
</{astag}>
"""
        return self.format(template, values, context)


    def render_tmpl_closebtn(self, values, context):
        """Dynamically render a part of the component's template
        """
        if values['content_id']:
            template = """
<div class="nj-toast__action">
  <button type="button" class="nj-icon-btn nj-icon-btn--lg {button_class}"
      aria-describedby="{content_id}" {button_props}>
    <span class="nj-sr-only">{txt_close}</span>
    <span aria-hidden="true" class="nj-icon-btn__icon material-icons">
      close
    </span>
  </button>
</div>
"""
            return self.format(template, values)
        return ''


    def render_tmpl_gauge(self, values, context):
        """Dynamically render a part of the component's template
        """
        if values['gauge']:
            template = """
<div class="nj-toast__gauge">
  <div class="nj-toast__gauge-bar {gauge_class}" {gauge_props}>
    <p class="nj-sr-only">{txt_gauge}</p>
  </div>
</div>
"""
            return self.format(template, values)
        return ''



class ToastText(Node):
    """Toast text component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    DEFAULT_TAG = 'p'
    "Rendered HTML tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-toast__text {class}" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values, context)


class ToastTitle(Node):
    """Toast title component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    DEFAULT_TAG = 'p'
    "Rendered HTML tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-toast__title {class}" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values, context)


class ToastContainer(Node):
    """Toast component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('fullwidth',)
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if values['label']:
            values['props'].append(('aria-label', values['label']))

        if self.eval(self.kwargs.get('fullwidth'), context):
            values['class'].append('nj-toast__container--full-width')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-toast__container {class}" role="region" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'Toast': Toast,
    'ToastText': ToastText,
    'ToastTitle': ToastTitle,
    'ToastContainer': ToastContainer,
}
