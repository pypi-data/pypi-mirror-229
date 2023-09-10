"""
Progress bar
============

See: https://www.engie.design/fluid-design-system/components/progress/

Progress bars allow users to know their task was successfully launched and the
system progresses towards task completion. They are a representation of a
progress status that evolves over time. As a general rule of thumb, use progress
bars when task completion takes longer than 1 second.
"""
from .base import Node

class ProgressBar(Node):
    """Progress bar component
    """
    NODE_PROPS = ('current', 'min', 'max', 'text')
    "Extended Template Tag arguments."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        if values['label']:
            values['props'].append(('aria-label', values['label']))

        current = self.eval(self.kwargs.get('current', 0), context)
        value_min = self.eval(self.kwargs.get('min', 0), context)
        value_max = self.eval(self.kwargs.get('max', 100), context)

        percent = current * 100 / (value_max - value_min)
        if int(percent) == percent:
            percent = int(percent)
        else:
            percent = round(percent, 2)
        values['percent'] = percent

        values['text'] = self.eval(self.kwargs.get('text'), context)

        if percent:
            values['props'].append(('style', f'width: {percent}%'))
        values['props'].append(('aria-valuenow', current))
        values['props'].append(('aria-valuemin', value_min))
        values['props'].append(('aria-valuemax', value_max))


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<div class="nj-progress">
  <div class="nj-progress__bar {class}" role="progressbar" {props}>
    <span class="nj-sr-only">{percent}%</span>
  </div>
  {tmpl_text}
</div>
"""
        return self.format(template, values, context)


    def render_tmpl_text(self, values, context):
        """Dynamically render a part of the component's template
        """
        if not values['text']:
            return ''

        tpl = '<div aria-hidden="true" class="nj-progress__text">{text}</div>'
        return tpl.format(text=values['text'])


components = {
    'Progress': ProgressBar,
}
