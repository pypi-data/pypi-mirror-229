"""
Card
====

See: https://www.engie.design/fluid-design-system/components/card/

Cards help bring hierarchy and visual consistency to the information displayed
on a page, especially when the content is heterogenous. They are excellent ways
to display rich media content like images or videos or to highlight
action-required elements.
"""
from .base import Node

class Card(Node):
    """Card component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    SLOTS = ('date', 'details', 'description', 'growth', 'header', 'image',
            'number', 'price', 'subtitle', 'title')
    "Named children."
    MODES = ('default', 'cover')
    "Available variants."
    NODE_PROPS = ('border', 'variant', 'align')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('body',)
    "Prepare xxx_class and xxx_props values."
    POSSIBLE_VARIANTS = ('horizontal',)
    "Possible values for variant argument."
    POSSIBLE_ALIGNS = ('center',)
    "Possible values for align argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates.
        """
        if self.eval(self.kwargs.get('border'), context):
            values['class'].append('nj-card--border')

        variant = self.eval(self.kwargs.get('variant'), context)
        if variant in self.POSSIBLE_VARIANTS:
            values['class'].append(f'nj-card--{variant}')

        align = self.eval(self.kwargs.get('align'), context)
        if align in self.POSSIBLE_ALIGNS:
            values['body_class'].append(f'text-{align}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-card {class}" {props}>
  {slot_image}
  {slot_header}
  <div class="nj-card__body {body_class}" {body_props}>
    {slot_details}
    {slot_title}
    {slot_price}
    {child}
    {slot_number}
    {slot_growth}
    {slot_subtitle}
    {slot_date}
  </div>
</{astag}>
"""
        return self.format(template, values, context)


    def render_cover(self, values, context):
        """Html output of the component
        """
        template = """
<a class="nj-card nj-card--cover {class}" {props}>
  <div class="nj-card__body {body_class}" {body_props}>
    <div class="nj-card__overlay">
      {slot_title}
      <span class="material-icons" aria-hidden="true">arrow_forward</span>
      {slot_description}
    </div>
  </div>
</a>
"""
        return self.format(template, values, context)


    def render_slot_title(self, values, context):
        """Render html of the slot.
        """
        if not values['astag']:
            values['astag'] = 'h4'
        tmpl = """
<{astag} class="nj-card__title {class}" {props}>
  {child}
</{astag}>
"""
        return tmpl.format(**values)


    def render_slot_subtitle(self, values, context):
        """Render html of the slot.
        """
        if not values['astag']:
            values['astag'] = 'h4'
        tmpl = """
<{astag} class="nj-card__subtitle {class}" {props}>
  {child}
</{astag}>
"""
        return tmpl.format(**values)


    def render_slot_header(self, values, context):
        """Render html of the slot.
        """
        tmpl = '<div class="nj-card__header {class}" {props}>{child}</div>'
        return tmpl.format(**values)


    def render_slot_description(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<p class="nj-card__description {class}" {props}>
  {child}
</p>
"""
        return tmpl.format(**values)


    def render_slot_details(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<p class="nj-card__details {class}" {props}>
  {child}
</p>
"""
        return tmpl.format(**values)


    def render_slot_image(self, values, context):
        """Render html of the slot.
        """
        tmpl = """
<div class="nj-card__img-wrapper {class}" {props}>
  {child}
</div>
"""
        return tmpl.format(**values)


    def render_slot_price(self, values, context):
        """Render html of the slot.
        """
        tmpl = '<div class="nj-card__price {class}" {props}>{child}</div>'
        return tmpl.format(**values)


    def render_slot_number(self, values, context):
        """Render html of the slot.
        """
        tmpl = '<p class="nj-card__number {class}" {props}>{child}</p>'
        return tmpl.format(**values)


    def render_slot_growth(self, values, context):
        """Render html of the slot.
        """
        tmpl = '<p class="nj-card__growth {class}" {props}>{child}</p>'
        return tmpl.format(**values)


    def render_slot_date(self, values, context):
        """Render html of the slot.
        """
        tmpl = '<p class="nj-card__date {class}" {props}>{child}</p>'
        return tmpl.format(**values)


class CardImage(Node):
    """Card img component
    """
    def render_default(self, values, context):
        """Html output of the component
        """
        template = '<img class="nj-card__img {class}" {props}>'
        return self.format(template, values)


class CardList(Node):
    """Card list component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('variant',)
    "Extended Template Tag arguments."
    POSSIBLE_VARIANTS = ('columns', 'deck')
    "Possible values for variant argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates.
        """
        variant = self.eval(self.kwargs.get('variant'), context)
        if variant in self.POSSIBLE_VARIANTS:
            values['class'].append(f'nj-card-{variant}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = '<div class="{class}" {props}>{child}</div>'
        return self.format(template, values)


components = {
    'Card': Card,
    'CardList': CardList,
    'CardImage': CardImage,
}
