"""
Status-indicator
================

Status indicators are dynamic pieces of information that should be used to
convey the status of a person, an object or a process. They do not require any
user actions to be updated, and are usually part of a larger component.
"""
from django.utils.translation import gettext as _
#-
from .base import Node

class StatusIndicator(Node):
    """Status indicator component
    """
    NODE_PROPS = ('status', 'size', 'nolabel')
    "Extended Template Tag arguments."
    POSSIBLE_STATUSES = ('offline', 'online', 'away', 'do-not-disturb', 'busy',
            'unknown', 'error', 'success', 'warning', 'in-progress', 'info')
    "Possible values for status argument."
    POSSIBLE_SIZES = ('sm', 'lg')
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        status = self.eval(self.kwargs.get('status'), context)
        if status:
            values['class'].append(f'nj-status-indicator--{status}')
        if status == 'offline':
            values['txt_label'] =  _("Offline")
        elif status == 'online':
            values['txt_label'] =  _("Online")
        elif status == 'away':
            values['txt_label'] =  _("Away")
        elif status == 'do-not-disturb':
            values['txt_label'] =  _("Do not disturb")
        elif status == 'busy':
            values['txt_label'] =  _("Busy")
        elif status == 'unknown':
            values['txt_label'] =  _("Unknown")
        elif status == 'error':
            values['txt_label'] =  _("Error")
        elif status == 'success':
            values['txt_label'] =  _("Success")
        elif status == 'warning':
            values['txt_label'] =  _("Warning")
        elif status == 'in-progress':
            values['txt_label'] =  _("In progress")
        elif status == 'info':
            values['txt_label'] =  _("Info")
        else:
            values['txt_label'] =  _("Online")

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-status-indicator--{size}')


    def render_default(self, values, context):
        """Html output of the component
        """
        if self.eval(self.kwargs.get('nolabel'), context):
            template = """
<{astag} aria-hidden="true" class="nj-status-indicator {class}" {props}>
  <div class="nj-status-indicator__svg"></div>
</{astag}>
"""
        else:
            template = """
<{astag} class="nj-status-indicator {class}" {props}>
  <div class="nj-status-indicator__svg"></div>
  <p class="nj-status-indicator__text">{txt_label}</p>
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'StatusIndicator': StatusIndicator,
}
