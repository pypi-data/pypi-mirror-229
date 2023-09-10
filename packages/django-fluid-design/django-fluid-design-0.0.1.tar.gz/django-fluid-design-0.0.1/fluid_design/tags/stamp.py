"""
Stamp
=====

See: https://www.engie.design/fluid-design-system/components/stamp/

Stamp is a special brand identity component for Act with ENGIE operation
"""
from .base import Node

class Stamp(Node):
    """Stamp component
    """
    NODE_PROPS = ('id', 'gradient', 'shadow')
    "Extended Template Tag arguments."
    CLASS_AND_PROPS = ('circle',)
    "Prepare xxx_class and xxx_props values."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['label_parts'] = values['label'].split(' ', 3)
        values['gradient'] = self.eval(self.kwargs.get('gradient'), context)
        if values['gradient']:
            values['circle_props'].append(('fill',
                    f"url(#{values['id']}-gradient)"))
        else:
            values['circle_props'].append(('fill', '#fff'))

        if self.eval(self.kwargs.get('shadow'), context):
            values['class'].append('nj-stamp--shadow')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<svg xmlns="http://www.w3.org/2000/svg" class="nj-stamp {class}" {props}>
  <defs>
    {tmpl_gradient}
    <mask id="{id}-mask" x="0" y="0" width="100%" height="100%">
      <circle class="nj-stamp__overlay" cx="85" cy="85" r="85"/>
      <text class="nj-stamp__text" y="67" transform="translate(85)">
        {tmpl_label1}
        {tmpl_label2}
        {tmpl_label3}
      </text>
    </mask>
  </defs>
  <circle cx="85" cy="85" r="85" mask="url(#{id}-mask)" {circle_props}/>
</svg>
"""
        return self.format(template, values, context)


    def render_tmpl_gradient(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if values['gradient']:
            stops = []
            grads = [x for x in values['gradient'].split(' ') if x.strip()]
            for ii, grad in enumerate(grads):
                pos = int(ii / (len(grads) - 1) * 100)
                stops.append(f'<stop offset="{pos}%" stop-color="{grad}"/>')
            values['stops'] = '\n'.join(stops)
            template = """
<linearGradient id="{id}-gradient" x1="0" x2="1" y1="0" y2="1">
  {stops}
</linearGradient>
"""
            return self.format(template, values)
        return ''


    def render_tmpl_label1(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if len(values['label_parts']) > 0:
            label = values['label_parts'][0]
            return f'<tspan x="0" text-anchor="middle">{label}</tspan>'
        return ''


    def render_tmpl_label2(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if len(values['label_parts']) > 1:
            label = values['label_parts'][1]
            return f'<tspan x="0" text-anchor="middle" dy="28">{label}</tspan>'
        return ''


    def render_tmpl_label3(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if len(values['label_parts']) > 2:
            label = values['label_parts'][2]
            return f'<tspan x="0" text-anchor="middle" dy="28">{label}</tspan>'
        return ''


components = {
    'Stamp': Stamp,
}
