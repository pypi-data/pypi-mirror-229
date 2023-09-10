"""
Tag
===

See: https://www.engie.design/fluid-design-system/components/tag/

Tags are used to show the criteria used to filter information. They can be
combined and used in every color of ENGIE’s palette.
Tags are used to visually label UI objects and elements for quick recognition.
For example, we can use them on cards, on tables, on form, etc. 
"""

from django.utils.translation import gettext as _
#-
from .base import COLORS, Node

class Tag(Node):
    """Tag component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon',)
    "Named children."
    MODES = ('default', 'anchor')
    "Available variants."
    NODE_PROPS = ('delete', 'disabled', 'href', 'size', 'color', 'inversed')
    "Extended Template Tag arguments."
    POSSIBLE_SIZES = ('sm', 'lg')
    "Possible values for size argument."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."
    CLASS_AND_PROPS = ('child', 'button')
    "Prepare xxx_class and xxx_props values."

    # Parent Tags can set the arguments of their children Tags, in effect
    # changing their appearance.
    CATCH_PROPS = ('tag_kwargs',)

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['txt_remove'] = _("Remove tag")

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-tag--{size}')

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-tag--{color}')

        href = self.eval(self.kwargs.get('href'), context)
        disabled =  self.eval(self.kwargs.get('disabled'), context)

        if self.mode == 'anchor':
            values['props'].append(('href', href))

            if disabled:
                values['class'].append('nj-tag--disabled')
                values['props'].append(('aria-disabled', 'true'))

        elif disabled:
            values['class'].append('nj-tag--disabled')
            values['child_tag'] = 'a'
            values['child_class'].append('nj-tag__text')
            values['child_props'].append(('role', 'link'))
            values['child_props'].append(('aria-disabled', 'true'))
        elif href:
            values['child_tag'] = 'a'
            values['child_props'].append(('href', href))
            values['child_class'].append('nj-tag__link')
        else:
            values['child_tag'] = 'span'
            values['child_class'].append('nj-tag__text')

        if not self.eval(self.kwargs.get('inversed'), context):
            values['button_class'].append('nj-icon-btn--secondary')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-tag {class}" {props}>
  <{child_tag} class="{child_class}" {child_props}>{child}</{child_tag}>
  {slot_icon}
  {tmpl_delete}
</{astag}>
"""
        return self.format(template, values, context)


    def render_anchor(self, values, context):
        """Html output of the component
        """
        template = """
<a class="nj-tag {class}" {props}>
  <span class="nj-tag__text">{child}</span>
  {slot_icon}
  {tmpl_delete}
</a>
"""
        return self.format(template, values, context)


    def render_tmpl_delete(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not self.eval(self.kwargs.get('delete'), context):
            return ''

        template = """
<button type="button" class="nj-tag__close nj-icon-btn nj-icon-btn--sm {button_class}">
  <span class="nj-sr-only">{txt_remove} {child}</span>
  <span aria-hidden="true" class="nj-icon-btn__icon material-icons">close</span>
</button>
"""
        return template.format(**values)


    def render_slot_icon(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<span class="nj-tag__icon {class}" aria-hidden="true" {props}>
  {child}
</span>
"""
        return tmpl.format(**values)


components = {
    'Tag': Tag,
}
