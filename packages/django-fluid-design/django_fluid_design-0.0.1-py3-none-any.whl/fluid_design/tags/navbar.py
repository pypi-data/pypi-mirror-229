"""
Navbar
======

See: https://www.engie.design/fluid-design-system/components/navbar/

The navbar helps users know where they are on the product and quickly access
other pages and features at any moment. This version is useful for application
websites with few sections.

Please check also the Header component for more possibilities.
"""
import os
import re
#-
from django.utils.translation import gettext as _
#-
from .base import COLORS, Node

class Navbar(Node):
    """Navbar component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    MODES = ('collapsible', 'simple')
    "Available variants."
    SLOTS = ('after',)
    "Named children."
    NODE_PROPS = ('id', 'href', 'logo_src', 'logo_alt', 'logo_width',
        'logo_height', 'expand', 'transparent', 'size', 'color')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'nav'
    "Rendered HTML tag."
    CLASS_AND_PROPS = ('logo',)
    "Prepare xxx_class and xxx_props values."
    POSSIBLE_EXPANDS = ('xl',)
    "Possible values for expand argument."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."
    POSSIBLE_SIZES = ('sm',)
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates.
        """
        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-navbar--{size}')

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-navbar--{color}')

        if self.eval(self.kwargs.get('transparent'), context):
            values['class'].append('nj-navbar--transparent')
        else:
            values['class'].append('nj-navbar--shadow')

        expand = self.eval(self.kwargs.get('expand'), context)
        if expand in self.POSSIBLE_EXPANDS:
            values['class'].append(f'nj-navbar--expand-{expand}')
        elif expand is True:
            values['class'].append('nj-navbar--expand')


    def render_collapsible(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-navbar {class}" {props}>
  {tmpl_logo}
  <button class="nj-navbar__toggler" type="button" data-toggle="collapse"
      data-target="#{id}">
    <span class="nj-navbar__toggler-icon material-icons">menu</span>
  </button>
  <div class="nj-navbar--collapse nj-collapse" id="{id}">
    <ul class="nj-navbar__nav">
      {child}
    </ul>
    {slot_after}
  </div>
</{astag}>
"""
        return self.format(template, values, context)


    def render_simple(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-navbar {class}" {props}>
  {tmpl_logo}
  <ul class="nj-navbar__nav">
    {child}
  </ul>
  {slot_after}
</{astag}>
"""
        return self.format(template, values, context)


    def render_tmpl_logo(self, values, context):
        """Dynamically render a part of the component's template
        """
        logo_src = self.eval(self.kwargs.get('logo_src'), context)
        if not logo_src:
            return ''
        logo_alt = self.eval(self.kwargs.get('logo_alt', 'home'), context)
        logo_width = self.eval(self.kwargs.get('logo_width', ''), context)
        logo_height = self.eval(self.kwargs.get('logo_height', ''), context)

        _, fileext = os.path.splitext(logo_src)
        fileext = re.split('[#?]', fileext, 1)[0]
        if fileext == '.svg':
            tpl_image = f"""
<svg class="nj-navbar__logo" aria-label="{logo_alt}">
  <use href="{logo_src}" />
</svg>
"""
        else:
            tpl_image = f"""
<img class="nj-navbar__logo" src="{logo_src}" alt="{logo_alt}"
    width="{logo_width}" height="{logo_height}">
"""
        href = self.eval(self.kwargs.get('href', '/'), context)
        return f'<a class="nj-navbar__brand" href="{href}">{tpl_image}</a>'


class NavbarMenu(Node):
    """Navbar item component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('active', 'disabled', 'icon')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'a'
    "Rendered HTML tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if self.eval(self.kwargs.get('icon'), context):
            values['class'].append('nj-navbar__nav-link--icon')

        if self.eval(self.kwargs.get('active'), context):
            values['class'].append('active')

        if self.eval(self.kwargs.get('disabled'), context):
            values['class'].append('disabled')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-navbar__nav-item">
  <{astag} class="nj-navbar__nav-link {class}" {props}>
    {child}
  </{astag}>
</li>
"""
        return self.format(template, values, context)


class NavbarSearch(Node):
    """Navbar search form component
    """
    NODE_PROPS = ('action', 'method', 'id', 'color')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('form', 'icon')
    "Prepare xxx_class and xxx_props values."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['txt_search'] = _("Search")
        values['txt_placeholder'] = _("Enter your query...")
        values['txt_close'] = _("Close")

        act = self.eval(self.kwargs.get('action'), context)
        if act:
            values['form_props'].append(('action', act))
        method = self.eval(self.kwargs.get('method'), context)
        if method:
            values['form_props'].append(('method', method))

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['icon_class'].append(f'nj-icon-material--{color}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<form class="nj-navbar__search nj-collapse {form_class}" id="{id}" {form_props}>
  <input class="nj-form-control nj-navbar__search-input {class}" type="text"
      id="{id}-input" placeholder="{txt_placeholder}" {props}>
  <button type="submit" class="nj-btn nj-navbar__search-button">
    {txt_search}
  </button>
  <a href="#" aria-label="{txt_close}" data-dismiss="#{id}"
      class="nj-navbar__nav-link nj-navbar__nav-link--icon nj-collapse-inline__close">
    <span aria-hidden="true" class="material-icons nj-icon-material {icon_class}"
        {icon_props}>
      close
    </span>
  </a>
</form>
"""
        return self.format(template, values)


class NavbarSearchIcon(Node):
    """Navbar search button component for navbar search form
    """
    NODE_PROPS = ('target', 'color')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('icon',)
    "Prepare xxx_class and xxx_props values."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['target'] = self.eval(self.kwargs.get('target'), context)

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['icon_class'].append(f'nj-icon-material--{color}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-navbar__nav-item">
  <a class="nj-navbar__nav-link nj-navbar__nav-link--icon {class}"
      data-toggle="collapse" href="#{target}" aria-expanded="false"
      aria-controls="{target}" {props}>
    <span aria-hidden="true" class="material-icons nj-icon-material {icon_class}"
        {icon_props}>
      search
    </span>
  </a>
</li>
"""
        return self.format(template, values)


components = {
    'Navbar': Navbar,
    'N_Menu': NavbarMenu,
    'N_MenuSearch': NavbarSearchIcon,
    'N_Search': NavbarSearch,
}
