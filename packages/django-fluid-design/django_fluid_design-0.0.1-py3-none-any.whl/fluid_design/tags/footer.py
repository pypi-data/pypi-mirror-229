"""
Footer
======

See: https://www.engie.design/fluid-design-system/components/footer/

Footer is mainly used for links and legal information.
"""
from .base import Node

class Footer(Node):
    """Footer component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('banner', 'menu', 'social')
    "Named children."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<footer class="nj-footer {class}" role="contentinfo" {props}>
  <div class="container">
    {slot_banner}
    {slot_menu}
    <ul class="nj-footer__links">
      {child}
    </ul>
    {slot_social}
  </div>
</footer>
"""
        return self.format(template, values, context)


    def render_slot_banner(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<div class="nj-footer__baseline {class}" {props}>
  {child}
</div>
<hr>
"""
        return tmpl.format(**values)


    def render_slot_menu(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<div class="nj-footer__menu {class}" {props}>
  {child}
</div>
<hr>
"""
        return tmpl.format(**values)


    def render_slot_social(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<ul class="nj-footer__social {class}" {props}>
  {child}
</ul>
"""
        return tmpl.format(**values)


class FooterLink(Node):
    """Footer link component
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
  <{astag} class="nj-link nj-link--contextual {class}" {props}>
    {child}
  </{astag}>
</li>
"""
        return self.format(template, values, context)


class FooterSocial(Node):
    """Footer social link component
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
  <{astag} class="nj-footer__social-link {class}" {props}>
    {child}
  </{astag}>
</li>
"""
        return self.format(template, values, context)


class FooterMenuSection(Node):
    """Footer menu section component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."

    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-footer__menu-section">
  {tmpl_label}
  <ul class="nj-footer__links-list">
    {child}
  </ul>
</div>
"""
        return self.format(template, values, context)


    def render_tmpl_label(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not values.get('label'):
            return ''
        template = '<h2 class="nj-footer__links-list-title">{label}</h2>'
        return self.format(template, values)


components = {
    'Footer': Footer,
    'FooterLink': FooterLink,
    'FooterSocial': FooterSocial,
    'FooterMenu': FooterMenuSection,
}
