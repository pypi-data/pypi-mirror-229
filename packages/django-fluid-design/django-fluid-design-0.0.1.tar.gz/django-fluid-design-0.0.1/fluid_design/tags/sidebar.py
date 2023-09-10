"""
Sidebar
=======

See: https://www.engie.design/fluid-design-system/components/sidebar/

Sidebar can contain the entire content of the product and allows users a quick
access to a specific piece of content. The left arrow allows the user to retract
or expand the sidebar.
"""
from .base import Node

class Sidebar(Node):
    """Sidebar component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('footer',)
    "Named children."
    NODE_PROPS = ('href', 'logo_src', 'logosm_src', 'logo_width',
            'logosm_width', 'logo_height', 'logosm_height', 'logo_alt',
            'folded', 'nomotion')
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['logo_width'] = self.eval(self.kwargs.get('logo_width', 100),
                context) or ''
        values['logo_height'] = self.eval(self.kwargs.get('logo_height'),
                context) or ''
        values['logosm_width'] = self.eval(self.kwargs.get('logosm_width'),
                context) or ''
        values['logosm_height'] = self.eval(
                self.kwargs.get('logosm_height', 36), context) or ''
        values['logo_src'] = self.eval(self.kwargs.get('logo_src'), context)
        values['logosm_src'] = self.eval(self.kwargs.get('logosm_src',
                values['logo_src']),
                context)
        values['logo_alt'] = self.eval(self.kwargs.get('logo_alt', ''), context)
        values['href'] = self.eval(self.kwargs.get('href', '#'), context)

        if self.eval(self.kwargs.get('folded'), context):
            values['class'].append('nj-sidebar--folded')
        if self.eval(self.kwargs.get('nomotion'), context):
            values['class'].append('nj-sidebar--no-motion')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-sidebar {class}" data-close-on-interact-out="true" {props}>
  {tmpl_logo}
  <nav class="nj-sidebar__navigation">
    <ul class="nj-list-group nj-list-group--sm nj-list-group--no-border nj-list-group--spaced-items">
      {child}
    </ul>
  </nav>
  {slot_footer}
  <ul class="nj-sidebar__collapse nj-list-group nj-list-group--sm nj-list-group--no-border">
    <li class="nj-list-group__item nj-list-group__item--clickable nj-list-group__item--no-border">
      <button data-toggle="sidebar" data-target="#{id}" aria-pressed="false">
        <span aria-hidden="true"
            class="material-icons nj-list-group__item-icon nj-sidebar__fold-btn">
          chevron_left
        </span>
        <span class="nj-list-group__item-content">Close</span>
      </button>
    </li>
  </ul>
</div>
"""
        return self.format(template, values, context)


    def render_tmpl_logo(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not values['logo_src']:
            return ''
        template = """
<a class="nj-sidebar__brand" href="{href}" title="{logo_alt}">
  <img class="nj-sidebar__logo" src="{logo_src}" alt="{logo_alt}"
      width="{logo_width}" height="{logo_height}">
  <img class="nj-sidebar__logo--folded" src="{logosm_src}" alt="{logo_alt}"
      width="{logosm_width}" height="{logosm_height}">
</a>
"""
        return self.format(template, values)


    def render_slot_footer(self, values, context):
        """Dynamically render a part of the component's template
        """
        template = """
<nav class="nj-sidebar__navigation nj-sidebar__navigation--footer {class}"
    {props}>
  <ul class="nj-list-group nj-list-group--sm nj-list-group--no-border nj-list-group--spaced-items">
    <div class="nj-sidebar__divider"></div>
    {child}
  </ul>
</nav>
"""
        return self.format(template, values)


class SidebarMenu(Node):
    """Sidebar menu component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('icon',)
    "Named children."
    NODE_PROPS = ('href', 'badge', 'arrow', 'current')
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        context['icon_kwargs'] = {
            'class': 'nj-list-group__item-icon',
        }

        values['href'] = self.eval(self.kwargs.get('href', '#'), context)
        values['badge'] = self.eval(self.kwargs.get('badge'), context)

        if self.eval(self.kwargs.get('current'), context):
            values['class'].append('active')
            values['props'].append(('aria-current', 'true'))


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<li class="nj-list-group__item nj-list-group__item--clickable nj-list-group__item--right-border {class}"
    {props}>
  <a href="{href}">
    {slot_icon}
    <span class="nj-list-group__item-content">{child}</span>
    {tmpl_after}
  </a>
</li>
"""
        return self.format(template, values, context)


    def render_tmpl_after(self, values, context):
        """Dynamically render a part of the component's template
        """
        if values['badge']:
            template = """
<p class="nj-badge nj-list-group__item-right-content">{badge}</p>
"""
        elif self.eval(self.kwargs.get('arrow'), context):
            template = """
<span aria-hidden="true"
    class="material-icons nj-list-group__item-icon nj-list-group__item-right-content">
  chevron_right
</span>
"""
        else:
            return ''
        return self.format(template, values)


components = {
    'Sidebar': Sidebar,
    'S_Menu': SidebarMenu,
}
