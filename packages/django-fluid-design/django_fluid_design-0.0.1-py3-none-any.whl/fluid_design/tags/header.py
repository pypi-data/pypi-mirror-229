"""
Header
======

See: https://www.engie.design/fluid-design-system/components/header/

The header is a structuring element of ENGIE's identity. It is the main
navigation of a website. This version is primarily intended for the corporate
website with many sections.
Please check also the Navbar component for a more compact version.
"""
from django.utils.translation import gettext as _
#-
from .base import COLORS, Node

class Header(Node):
    """Header component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('head_first', 'head_last', 'search')
    "Named children."
    NODE_PROPS = ('fixed', 'size', 'scroll', 'expand', 'href', 'logo_src',
        'logosm_src', 'logo_width', 'logosm_width', 'logo_height',
        'logosm_height', 'logo_alt')
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'header'
    "Rendered HTML tag."
    POSSIBLE_SIZES = ('sm',)
    "Possible values for size argument."
    POSSIBLE_SCROLLS = ('sm',)
    "Possible values for scroll argument."
    POSSIBLE_EXPANDS = ('lg',)
    "Possible values for expand argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['logo_width'] = self.eval(self.kwargs.get('logo_width'),
                context) or ''
        values['logo_height'] = self.eval(self.kwargs.get('logo_height', 48),
                context) or ''
        values['logosm_width'] = self.eval(self.kwargs.get('logosm_width'),
                context) or ''
        values['logosm_height'] = self.eval(
                self.kwargs.get('logosm_height', 32), context) or ''
        values['logo_src'] = self.eval(self.kwargs.get('logo_src'), context)
        values['logosm_src'] = self.eval(self.kwargs.get('logosm_src',
                values['logo_src']),
                context)
        values['logo_alt'] = self.eval(self.kwargs.get('logo_alt', ''), context)
        values['href'] = self.eval(self.kwargs.get('href', '#'), context)

        if self.eval(self.kwargs.get('fixed'), context):
            values['class'].append('nj-header--fixed')

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SCROLLS:
            values['class'].append(f'nj-header--{size}')

        scroll = self.eval(self.kwargs.get('scroll'), context)
        if scroll in self.POSSIBLE_SCROLLS:
            values['class'].append(f'nj-header--scroll-{scroll}')

        expand = self.eval(self.kwargs.get('expand'), context)
        if expand in self.POSSIBLE_EXPANDS:
            values['class'].append(f'nj-header--expand-{expand}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-header {class}" {props}>
  <div class="nj-header__group">
    {tmpl_head}
    <nav class="container">
      <div class="nj-header__nav-burger" aria-label="menu"
          aria-expanded="false">
        <button><div></div></button>
      </div>
      {tmpl_head_logosm}
      <ul class="nj-header__nav nj-header__nav--panel">
        {child}
      </ul>
      {slot_search}
    </nav>
  </div>
</{astag}>
"""
        return self.format(template, values, context)


    def render_tmpl_head(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not (values['logo_src'] or 'head_first' in self.slots or\
                'head_last' in self.slots):
            return ''
        tmpl = """
<div class="nj-header__head">
  {slot_head_first}
  {tmpl_head_logo}
  {slot_head_last}
</div>
<hr class="m-0">
"""
        return self.format(tmpl, values, context)


    def render_tmpl_head_logo(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not values['logo_src']:
            return ''
        tmpl = """
<a href="{href}" class="nj-header__logo">
  <img src="{logo_src}" alt="{logo_alt}" width="{logo_width}"
      height="{logo_height}">
</a>
"""
        return tmpl.format(**values)


    def render_tmpl_head_logosm(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not values['logosm_src']:
            return ''
        tmpl = """
<div class="nj-header__nav-logo--reduced">
  <a href="{href}">
    <img src="{logosm_src}" alt="{logo_alt}" width="{logosm_width}"
        height="{logosm_height}">
  </a>
</div>
"""
        return tmpl.format(**values)


class HeaderHeadLink(Node):
    """Header language link component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('active',)
    "Extended Template Tag arguments."
    DEFAULT_TAG = 'a'
    "Rendered HTML tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if self.eval(self.kwargs.get('active'), context):
            values['class'].append('nj-header__head-link--active')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-header__head-link {class}" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values)


class HeaderMenu(Node):
    """Header nav item component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('submenu',)
    "Named children."
    NODE_PROPS = ('active',)
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('wrapper',)
    "Prepare xxx_class and xxx_props values."
    DEFAULT_TAG = 'a'
    "Rendered HTML tag."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if self.eval(self.kwargs.get('active'), context):
            values['wrapper_class'].append('active')


    def after_prepare(self, values, context):
        """Simplifying values meant for rendering templates.
        """
        super().after_prepare(values, context)

        slot = self.slots.get('submenu')
        if slot:
            slot.kwargs.setdefault('label', values['child'])


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-header__nav-item {wrapper_class}" {wrapper_props}>
  <{astag} class="nj-header__nav-link {class}" {props}>
    {child} {tmpl_subarrow}
  </{astag}>
  {slot_submenu}
</li>
"""
        return self.format(template, values, context)


    def render_slot_submenu(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<div class="nj-header__menu nj-header__nav--panel">
  <a class="nj-header__menu-return">
    <i class="nj-header__menu-arrow-left material-icons md-24">
      keyboard_arrow_left
    </i>
    {label}
  </a>
  {child}
</div>
"""
        return tmpl.format(**values)


    def render_tmpl_subarrow(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not self.slots:
            return ''
        return """
<i class="nj-header__menu-arrow-right material-icons md-24">
  keyboard_arrow_right
</i>
"""


class HeaderMenuTag(HeaderMenu):
    """Header nav item as Tag component
    """
    NODE_PROPS = ('color', *HeaderMenu.NODE_PROPS)
    "Extended Template Tag arguments."
    POSSIBLE_COLORS = COLORS
    "Possible values for color argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        super().prepare(values, context)

        color = self.eval(self.kwargs.get('color'), context)
        if color in self.POSSIBLE_COLORS:
            values['class'].append(f'nj-tag--{color}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-header__nav-item {wrapper_class}" {wrapper_props}>
  <{astag} class="nj-tag {class}" {props}>
    {child}
  </{astag}>
</li>
"""
        return self.format(template, values)


class HeaderSubmenu(Node):
    """Header submenu navigation component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<ul class="nj-header__sub-nav">
  <li>
    <a href="#" class="nj-header__menu-title" aria-label="open"
        aria-expanded="false">
      {label}
      <i class="nj-header__menu-arrow-right material-icons md-24">
        keyboard_arrow_right
      </i>
    </a>
    <ul class="nj-header__nav--panel">
      <li>
        <a class="nj-header__menu-return">
          <i class="nj-header__menu-arrow-left material-icons md-24">
            keyboard_arrow_left
          </i>
          {label}
        </a>
      </li>
      {child}
    </ul>
  </li>
</ul>
"""
        return self.format(template, values)


class HeaderMenuLink(Node):
    """Header nav item component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    DEFAULT_TAG = 'a'
    "Rendered HTML tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li>
  <{astag} class="nj-header__menu-link {class}" {props}>
    {child}
  </{astag}>
</li>
"""
        return self.format(template, values)


class HeaderSearch(Node):
    """Header search component
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

        color = self.eval(self.kwargs.get('color', 'brand'), context)
        if color in self.POSSIBLE_COLORS:
            values['icon_class'].append(f'nj-icon-material--{color}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<a class="nj-header__search-icon" data-toggle="collapse"
    data-target="#collapse-search-bar-header" aria-expanded="false"
    aria-controls="collapse-search-bar-header">
  <i class="material-icons nj-icon-material {icon_class}" {icon_props}>
    search
  </i>
</a>
<form class="nj-header__search nj-collapse {form_class}" id="{id}" {form_props}>
  <input class="nj-form-control nj-navbar__search-input {class}" type="text"
      id="{id}-input" placeholder="{txt_placeholder}" {props}>
  <button type="submit" class="nj-btn nj-navbar__search-button">
    {txt_search}
  </button>
  <a data-target="#collapse-search-bar-header" class="nj-header__close"
      aria-label="{txt_close}" data-toggle="collapse">
    <i class="material-icons nj-icon-material {icon_class}" {icon_props}>
      close
    </i>
  </a>
</form>
"""
        return self.format(template, values)


components = {
    'Header': Header,
    'H_HeadLink': HeaderHeadLink,
    'H_Menu': HeaderMenu,
    'H_MenuTag': HeaderMenuTag,
    'H_Link': HeaderMenuLink,
    'H_Submenu': HeaderSubmenu,
    'H_Search': HeaderSearch,
}
