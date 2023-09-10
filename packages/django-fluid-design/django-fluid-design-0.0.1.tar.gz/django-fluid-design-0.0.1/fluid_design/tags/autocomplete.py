"""
Autocomplete
============

See: https://www.engie.design/fluid-design-system/components/autocomplete/

Autocomplete provides automated assistance to fill in form field values. It
allows the user to have suggestions while typing in the field.
"""
import json
#-
from django.utils.html import escape
from django.utils.translation import gettext as _
#-
from .base import FormNode

class Autocomplete(FormNode):
    """Autocomplete component
    """
    NODE_PROPS = ('data',)
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['txt_instruction'] = _("Use the UP / DOWN arrows to navigate "
                "within the suggestion list. Press Enter to select an option. "
                "On touch devices, use swipe to navigate and double tap to "
                "select an option")

        data = self.eval(self.kwargs.get('data'), context)
        if data:
            values['props'].append(('data-list', escape(json.dumps(data))))


    def prepare_element_props(self, props, context):
        """Prepare html attributes for rendering the form element.
        """
        props['role'] = 'combobox'
        props['aria-autocomplete'] = 'list'
        props['aria-controls'].append(f'{props["id"]}-list')
        props['aria-expanded'] = 'false'
        props['autocomplete'] = 'off'
        props['aria-describedby'] = f'{props["id"]}-autocomplete-instructions'
        props['class'].append('nj-form-item__field')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<p id="{id}-autocomplete-instructions" hidden>{txt_instruction}</p>
<div class="nj-form-item nj-form-item--autocomplete">
  <div class="nj-form-item__field-wrapper">
    {tmpl_element}
    {tmpl_label}

    <ul role="listbox" id="{id}-list" tabindex="-1"
        aria-label="Countries suggestions" hidden
        class="nj-form-item__list nj-list-group nj-list-group--no-border nj-list-group--sm">
      <li role="option" aria-selected="false" tabindex="-1"
          class="nj-list-group__item nj-list-group__item--clickable"/>
    </ul>

    <span aria-hidden="true" class="nj-form-item__icon material-icons">
      keyboard_arrow_down
    </span>
  </div>
</div>
"""
        return self.format(template, values, context)


components = {
    'Autocomplete': Autocomplete,
}
