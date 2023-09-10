"""
Checkbox
========

See: https://www.engie.design/fluid-design-system/components/checkbox/

A checkbox is an input control that allows the user to give a feedback by
choosing several items from a list of options. For example, you can use
checkbox when user may have to select multiple options from a list of items, or
when an explicit action is required to apply the settings in your product.
""" # pylint:disable=line-too-long

import logging
#-
from .base import ChoiceSetNode

_logger = logging.getLogger(__name__)


class CheckboxSet(ChoiceSetNode):
    """Checkbox component
    """
    NODE_PROPS = ('exclude', 'inline')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('item',)
    "Prepare xxx_class and xxx_props values."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if self.eval(self.kwargs.get('inline'), context):
            values['item_class'].append('nj-checkbox--inline')


    def render_default(self, values, context):
        """Html output of the component
        """
        if self.bound_field.errors:
            template = """
<fieldset class="nj-checkbox-group {class}" {props}>
  <legend class="nj-checkbox-group__legend">
    {label}
    {tmpl_errors}
  </legend>
  {tmpl_items}
</fieldset>
"""
        else:
            template = """
<fieldset class="nj-checkbox-group {class}" {props}>
  <legend class="nj-checkbox-group__legend">{label}</legend>
  {tmpl_items}
</fieldset>
"""
        return self.format(template, values, context)


    def render_tmpl_items(self, values, context):
        """Dynamically render a part of the component's template
        """
        template = """
<div class="nj-checkbox {class}">
  <label for="{id}">
    <input type="checkbox" name="{name}" id="{id}" value="{value}" {props}>
    {child}
  </label>
</div>
"""
        excludes = self.eval(self.kwargs.get('exclude', []), context)
        if isinstance(excludes, str):
            excludes = [x.strip() for x in excludes.split(';')]

        items = []
        for ii, (_, val, txt) in enumerate(self.choices()):
            options = {
                'id': '%s-%s' % (values['id'], ii + 1),
                'value': val,
                'child': txt,
                'name': self.bound_field.name,
                'class': values['item_class'],
            }
            props = []
            if self.check_test(val):
                props.append('checked')
            if val in excludes:
                options['class'] += ' nj-checkbox--disabled'
                props.append('disabled')
            if self.bound_field.errors:
                props.append('aria-invalid="true"')
                props.append(
                        'aria-describedby="{id}-errors"'\
                        .format(id=values['id']))
            options['props'] = ' '.join(props)
            items.append(self.format(template, options))

        return '\n'.join(items)


    def render_tmpl_errors(self, values, context):
        """Dynamically render a part of the component's template
        """
        template = """
<span id="{id}-errors" class="nj-checkbox__error">
  {child}
</span>
"""
        child = '\n'.join(self.bound_field.errors)
        return template.format(child=child, id=values['id'])


components = {
    'CheckboxSet': CheckboxSet,
}
