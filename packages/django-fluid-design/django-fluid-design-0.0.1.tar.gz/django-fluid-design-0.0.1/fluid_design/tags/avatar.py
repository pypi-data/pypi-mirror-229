"""
Avatar
======

See: https://www.engie.design/fluid-design-system/components/avatar/

Avatars are used to display a person's picture or initials. Avatars may help in
creating an emotional connection to the product and in validating that the
experience is indeed tailored for the current user.
"""
from django.utils.translation import gettext as _
#-
from .base import Node

class Avatar(Node):
    """Avatar component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    MODES = ('default', 'minimal')
    "Available variants."
    NODE_PROPS = ('size', 'initial', 'src', 'alt', 'clickable', 'badge',
            'status')
    "Extended Template Tag arguments."
    POSSIBLE_SIZES = ('sm', 'lg', 'xl')
    "Possible values for size argument."
    POSSIBLE_STATUSES = ('offline', 'away', 'busy', 'online')
    "Possible values for status argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        values['txt_badge'] = _("notifications")

        src = self.eval(self.kwargs.get('src'), context)
        if src:
            alt = self.eval(self.kwargs.get('alt'), context)
            values['src'] = src
            values['alt'] = alt
        else:
            initial = self.eval(self.kwargs.get('initial'), context)
            if initial:
                values['class'].append('nj-avatar--initials')
            else:
                values['class'].append('nj-avatar--default-icon')
            values['initial'] = initial

        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-avatar--{size}')
            values['size'] = size

        if self.eval(self.kwargs.get('clickable'), context):
            values['class'].append('nj-avatar--clickable')
            if 'astag' not in self.kwargs:
                values['astag'] = 'button'

        badge = self.eval(self.kwargs.get('badge'), context)
        try:
            values['badge'] = int(badge)
        except (ValueError, TypeError):
            pass

        status = self.eval(self.kwargs.get('status'), context)
        if status in self.POSSIBLE_STATUSES:
            values['status'] = status


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-avatar {class}" {props}>
  {tmpl_picture}
  {tmpl_initial}
  {tmpl_child}
  {tmpl_badge}
  {tmpl_status}
</{astag}>
"""
        return self.format(template, values, context)


    def render_minimal(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-avatar {class}" {props}>
  <div class="nj-avatar__picture">
    <img src="{src}" alt="{alt}">
  </div>
</{astag}>
"""
        return self.format(template, values, context)


    def render_tmpl_child(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if not values['child'].strip():
            return ''
        tmpl = '<span class="nj-sr-only">{child}</span>'
        return tmpl.format(**values)


    def render_tmpl_picture(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if not values.get('src'):
            return ''
        tmpl = """
<img class="nj-avatar__picture" src="{src}" alt="{alt}">
"""
        return tmpl.format(**values)


    def render_tmpl_initial(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if not values.get('initial'):
            return ''
        tmpl = """
<span class="nj-avatar__initials" aria-hidden="true">{initial}</span>
"""
        return tmpl.format(**values)


    def render_tmpl_badge(self, values, context):
        """Dynamically render a part of the component's template.
        """
        if not values.get('badge'):
            return ''
        if values.get('size') == 'sm':
            return ''

        badge_class = []

        if values.get('size') == 'xl':
            badge_class.append('nj-badge--lg')

        tmpl = """
<div class="nj-badge nj-badge--information {badge_class}">
  <p>{badge} <span class="nj-sr-only">{txt_badge}</span></p>
</div>
"""
        return tmpl.format(badge_class=' '.join(badge_class), **values)


    def render_tmpl_status(self, values, context):
        """Dynamically render a part of the component's template.
        """
        status = values.get('status')
        if not status:
            return ''

        status_class = []

        if status == 'offline':
            status_class.append('nj-status-indicator--offline')
            txt_status = _("Offline")
        elif status == 'away':
            status_class.append('nj-status-indicator--away')
            txt_status = _("Away")
        elif status == 'busy':
            status_class.append('nj-status-indicator--in-progress')
            txt_status = _("In progress")
        else:
            status_class.append('nj-status-indicator--online')
            txt_status = _("Online")

        size = values.get('size')
        if size == 'xl':
            status_class.append('nj-status-indicator--lg')
        elif size != 'lg':
            status_class.append('nj-status-indicator--sm')

        tmpl = """
<div class="nj-status-indicator {status_class}">
  <div class="nj-status-indicator__svg">
    <span class="nj-sr-only">{txt_status}</span>
  </div>
</div>
"""
        return tmpl.format(status_class=' '.join(status_class),
                txt_status=txt_status, **values)


class AvatarMore(Node):
    """Avatar more items component
    """
    NODE_PROPS = ('count', 'size', 'clickable')
    "Extended Template Tag arguments."
    POSSIBLE_SIZES = ('sm', 'lg', 'xl')
    "Possible values for size argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        size = self.eval(self.kwargs.get('size'), context)
        if size in self.POSSIBLE_SIZES:
            values['class'].append(f'nj-avatar--{size}')

        count = self.eval(self.kwargs.get('count'), context)
        if count:
            try:
                count = int(count)
            except ValueError:
                count = None

        values['count'] = count
        values['txt_more'] = _("Show {count} more user profiles")\
                .format(count=count)

        clickable = self.eval(self.kwargs.get('clickable'), context)
        if clickable:
            values['class'].append('nj-avatar--clickable')
            if 'astag' not in self.kwargs:
                values['astag'] = 'button'
        values['clickable'] = clickable


    def render_default(self, values, context):
        """Html output of the component
        """
        if values['clickable']:
            template = """
<{astag} class="nj-avatar nj-avatar--remaining-count {class}" {props}>
  <span aria-hidden="true">+{count}</span>
  <span class="nj-sr-only">{txt_more}</span>
</{astag}>
"""
        else:
            template = """
<{astag} class="nj-avatar nj-avatar--remaining-count {class}" {props}>
  +{count}
</{astag}>
"""
        return self.format(template, values)


class AvatarList(Node):
    """Avatar list component
    """
    WANT_CHILDREN = True
    "Template Tag needs closing end tag."
    NODE_PROPS = ('variant',)
    "Extended Template Tag arguments."
    POSSIBLE_VARIANTS = ('compact',)
    "Possible values for variant argument."

    def prepare(self, values, context):
        """Prepare values for rendering the templates
        """
        variant = self.eval(self.kwargs.get('variant'), context)
        if variant in self.POSSIBLE_VARIANTS:
            values['class'].append(f'nj-avatar-list--{variant}')


    def render_default(self, values, context):
        """Html output of the component
        """
        template = """
<{astag} class="nj-avatar-list {class}" {props}>
  {child}
</{astag}>
"""
        return self.format(template, values, context)


components = {
    'AvatarList': AvatarList,
    'Avatar': Avatar,
    'AvatarMore': AvatarMore,
}
