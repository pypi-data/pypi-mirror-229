"""
Segmented control
=================

See: https://www.engie.design/fluid-design-system/components/segmented-control/

Segmented controls are helpful to show closely-related options users can choose
from. They can be used to switch views for example.
"""
from .base import clean_attr_value, Node

class SegmentedControl(Node):
    """Segmented control component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    MODES = ('default', 'compact')
    "Available variants."
    NODE_PROPS = ('value', 'size')
    "Extended Template Tag arguments."
    POSSIBLE_SIZES = ('sm', 'lg')
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        context['segmented_control_button_kwargs'] = {}

        if self.mode == 'compact':
            context['segmented_control_button_kwargs']['compact'] = True

        if values['label']:
            values['props'].append(('aria-label', values['label']))

        value = self.eval(self.kwargs.get('value'), context)
        if value:
            values['props'].append(('data-value', value))

            context['segmented_control_button_kwargs']['selected'] = value

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-segmented-control--{size}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-segmented-control {class}" role="group" {props}>
  {child}
</div>
"""
        return self.format(template, values, context)


    def render_compact(self, values, context):
        """Html output of the component
        """
        return self.render_default(values, context)


class SegmentedControlButton(Node):
    """Segmented control button component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon',)
    "Named children."
    NODE_PROPS = ('value', 'selected', 'compact')
    "Extended Template Tag arguments."

    # Parent Tags can set the arguments of their children Tags, in effect
    # changing their appearance.
    CATCH_PROPS = ('segmented_control_button_kwargs',)

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        context['icon_icon_kwargs'] = {
            'class': 'nj-segmented-control-btn__icon',
        }

        values['value'] = self.eval(self.kwargs.get('value'), context)
        values['compact'] = self.eval(self.kwargs.get('compact'), context)


    def after_prepare(self, values, context):
        """Simplifying values meant for rendering templates.
        """
        cleaned_child = clean_attr_value(values['child'])
        if not values['value']:
            values['value'] = cleaned_child
        if values['value'] == self.eval(self.kwargs.get('selected'),
                context):
            values['props'].append(('aria-pressed', 'true'))
        else:
            values['props'].append(('aria-pressed', 'false'))

        if values['compact']:
            values['props'].append(('title', cleaned_child))

        super().after_prepare(values, context)


    def render_default(self, values, context):
        """Html output of the component
        """
        if 'icon' in self.slots:
            if values['compact']:
                template = """
<button class="nj-segmented-control-btn {class}" type="button"
    data-value="{value}" {props}>
  {slot_icon}
  <span class="nj-sr-only">{child}</span>
</button>
"""
            else:
                template = """
<button class="nj-segmented-control-btn {class}" type="button"
    data-value="{value}" {props}>
  {slot_icon}
  <span>{child}</span>
</button>
"""
        else:
            template = """
<button class="nj-segmented-control-btn {class}" type="button"
    data-value="{value}" {props}>
  {child}
</button>
"""
        return self.format(template, values, context)


components = {
    'SegmentedControl': SegmentedControl,
    'SegmentedControlBtn': SegmentedControlButton,
}
