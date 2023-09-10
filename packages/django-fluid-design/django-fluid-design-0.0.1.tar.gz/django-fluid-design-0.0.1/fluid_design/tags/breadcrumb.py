"""
Breadcrumb
==========

See: https://www.engie.design/fluid-design-system/components/breadcrumb/

Breadcrumbs should be used as soon as you structure information hierarchically.
Breadcrumbs provide users with their current location, help them find related
content and serve as secondary navigation.
""" # pylint:disable=line-too-long

from django.utils.translation import gettext as _
#-
from .base import Node

class Breadcrumb(Node):
    """Breadcrumb component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    DEFAULT_TAG = 'nav'
    "Rendered HTML tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates.
        """
        values['txt_breadcrumb'] = _("breadcrumb")
        tag = self.eval(self.kwargs.get('astag'), context)
        if tag and tag != 'nav':
            values['props'].append(('role', 'navigation'))


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} aria-label="{txt_breadcrumb}" {props}>
  <ol class="nj-breadcrumb">
    {child}
  </ol>
</{astag}>
"""
        return self.format(template, values)


class BreadcrumbItem(Node):
    """Breadcrumb item
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('href', 'current', 'isicon')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('link',)
    "Prepare xxx_class and xxx_props values."

    is_current = False

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['href'] = self.eval(self.kwargs.get('href', '#'), context)
        self.is_current = self.eval(self.kwargs.get('current', False), context)
        if self.is_current:
            values['props'].append(('aria-current', 'page'))

        if self.eval(self.kwargs.get('isicon', False), context):
            values['link_class'].append('nj-link-icon')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-breadcrumb__item {class}" {props}>{tmpl_item}</li>
"""
        return self.format(template, values, context)


    def render_tmpl_item(self, values, context):
        """Dynamically render a part of the component's template
        """
        if self.is_current:
            return values['child']

        template = """
<a href="{href}" class="nj-link nj-link--sm nj-link--grayed {link_class}"
    {link_props}>
  {child}
</a>
"""
        return self.format(template, values)


components = {
    'Breadcrumb': Breadcrumb,
    'BreadcrumbItem': BreadcrumbItem,
}
