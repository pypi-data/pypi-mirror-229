"""
Modal
=====

See: https://www.engie.design/fluid-design-system/components/modal/

Modal allows you to add dialogs to your site for lightboxes, user notifications,
or completely custom content.
"""
from django.utils.translation import gettext as _
#-
from .base import Node
from .button import Button

class Modal(Node):
    """Modal component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('title', 'footer', 'icon')
    "Named children."
    MODES = ('default', 'information', 'spinner')
    "Available variants."
    NODE_PROPS = ('append_to', 'vcenter', 'size', 'fcenter')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('dialog',)
    "Possible values for style argument."
    POSSIBLE_SIZES = ('sm',)
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['txt_close'] = _("Close")
        values['txt_loading'] = _("Loading...")
        values['props'].insert(0, ('role', 'alertDialog'))

        append_to = self.eval(self.kwargs.get('append_to'), context)
        if append_to:
            values['props'].append(('data-appendTo', append_to))

        if self.eval(self.kwargs.get('vcenter'), context):
            values['class'].append('nj-modal--vertical-centered')

        if self.mode == 'information':
            values['class'].append('nj-modal--information')

            context['icon_icon_kwargs'] = {
                'class': 'nj-modal__icon',
                'size': 'xxl',
            }
        elif self.mode == 'spinner':
            values['class'].append('nj-modal--information')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['dialog_class'].append(f'nj-modal--{size}')

        if self.eval(self.kwargs.get('fcenter'), context):
            values['footer_class'].append('nj-modal__footer--centered')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-modal fade {class}" aria-labelledby="{id}-title" {props}>
  <div class="nj-modal__dialog {dialog_class}" role="document" {dialog_props}>
    <div class="nj-modal__content">
      <div class="nj-modal__header">
        {slot_title}

        {% IconButton type="button" class="nj-modal__close" size="lg" data-dismiss="modal" %}
          {txt_close}
          {% Slot 'icon' %}
            <span aria-hidden="true" class="nj-icon-btn__icon material-icons">
              close
            </span>
          {% endSlot %}
        {% endIconButton %}
      </div>
      <div class="nj-modal__body">
        {child}
      </div>
      {slot_footer}
    </div>
  </div>
</div>
"""
        return self.format(template, values, context, is_template=True)


    def render_information(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-modal fade {class}" aria-labelledby="{id}-title" {props}>
  <div class="nj-modal__dialog {dialog_class}" role="document" {dialog_props}>
    <div class="nj-modal__content">
      <div class="nj-modal__header">
        {% IconButton type="button" class="nj-modal__close" size="lg" data-dismiss="modal" %}
          {txt_close}
          {% Slot 'icon' %}
            <span aria-hidden="true" class="nj-icon-btn__icon material-icons">
              close
            </span>
          {% endSlot %}
        {% endIconButton %}
      </div>
      <div class="nj-modal__body">
        {slot_icon}
        {slot_title}
        {child}
      </div>
      {slot_footer}
    </div>
  </div>
</div>
"""
        return self.format(template, values, context, is_template=True)


    def render_spinner(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-modal fade {class}" aria-labelledby="{id}-title" {props}>
  <div class="nj-modal__dialog {dialog_class}" role="document" {dialog_props}>
    <div class="nj-modal__content">
      <div class="nj-modal__body">
        <div class="nj-spinner nj-spinner--md nj-modal__loading-spinner"
            role="status">
          <span class="nj-sr-only">{txt_loading}</span>
        </div>
        {slot_title}
        {child}
      </div>
      {slot_footer}
    </div>
  </div>
</div>
"""
        return self.format(template, values, context)


    def render_slot_title(self, values, context):
        """Render html of the slot.
        """
        if not values['astag']:
            values['astag'] = 'h1'
        if self.mode == 'default':
            template = """
<{astag} id="{id}-title" class="nj-modal__title {class}" {props}>
  {slot_icon}
  {child}
</{astag}>
"""
        else:
            template = """
<{astag} id="{id}-title" class="nj-modal__title {class}" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values, context)


    def render_slot_footer(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<div class="nj-modal__footer {class}" {props}>
  {child}
</div>
"""
        return tmpl.format(**values)


class ModalButton(Button):
    """Modal trigger button component
    """
    NODE_PROPS = ('modal', *Button.NODE_PROPS)
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        super().prepare(values, context)

        modal_id = self.eval(self.kwargs['modal'], context)
        values['props'].append(('data-toggle', 'modal'))
        values['props'].append(('data-target', modal_id))


class ModalButtonDismiss(Button):
    """Modal close button component
    """
    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        super().prepare(values, context)

        values['props'].append(('data-dismiss', 'modal'))


components = {
    'Modal': Modal,
    'ModalBtn': ModalButton,
    'ModalCloseBtn': ModalButtonDismiss,
}
