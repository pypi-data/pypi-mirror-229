from django.contrib.sites.models import Site
from django.conf import settings
from django.templatetags.static import static

from mail_templated import EmailMessage

from .settings import appkit_settings
from .shortcuts import site_url_base

get_current_site = appkit_settings.CURRENT_SITE_ACCESSOR


class AppkitEmailMessage(EmailMessage):
    def __init__(self, template_name=None, context=dict, *args, **kwargs):
        if not 'site' in context and 'request' in context:
            context['site'] = get_current_site(context['request'])

        site = context.get('site')
        if not isinstance(site, Site):
            raise ValueError('Site could not be resolved from given context')
        
        if site.profile.icon:
            icon_url = site.profile.icon.image.thumbnail['192x192']
        else:
            icon_url = f'{site_url_base(site)}{static("images/icon/android-chrome-192x192.png")}'
        context['icon_url'] = icon_url

        if 'user' not in context and 'request' in context:
            context['user'] = context['request'].user

        super().__init__(template_name, context, *args, **kwargs)

    @property
    def from_email_address(self):
        return settings.DEFAULT_FROM_EMAIL

    def send(self, *args, **kwargs):
        from_email_sender = self.from_email_sender if hasattr(self, 'from_email_sender') else self.context['site'].name
        self.from_email = f'"{from_email_sender}" <{self.from_email_address}>'

        self.cc = kwargs.pop('cc', [])
        self.bcc = kwargs.pop('bcc', [])
        self.reply_to = kwargs.pop('reply_to', [])

        super(AppkitEmailMessage, self).send(*args, **kwargs)
