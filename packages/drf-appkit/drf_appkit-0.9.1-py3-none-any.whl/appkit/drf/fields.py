import base64
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.files import ImageFieldFile
from django.urls import resolve, reverse
from django.urls.exceptions import NoReverseMatch

from appkit.shortcuts import mimetype_for_file
from rest_framework.fields import CharField, IntegerField


class ContentTypeField(IntegerField):
    def get_attribute(self, instance):
        return ContentType.objects.get_for_model(instance).id


class DocumentPathField(CharField):
    def __init__(self, **kwargs):
        self.url_kwargs = kwargs.pop('url_kwargs', None)
        super().__init__(**kwargs)

    def get_namespaced_detail_url_name(self, instance, url_info):
        url_name = instance.get_detail_url_name()
        namespace = url_info.kwargs.get('namespace')
        if namespace:
            url_name = '{}:{}'.format(namespace, url_name)
        return url_name

    def get_detail_url_info(self, instance, url_info):
        namespace = url_info.kwargs['namespace']

        return {
            'kwargs': {'uuid': instance.uuid},
            'urlconf': f'app.{namespace}.urls',
        }


    def get_path(self, instance, url_info):
        try:
            detail_url_name = instance.get_detail_url_name()
        except NotImplementedError:
            return None

        detail_url_info = self.get_detail_url_info(instance, url_info)
        url = reverse(
            detail_url_name,
            kwargs=detail_url_info['kwargs'],
            urlconf=detail_url_info['urlconf']
        )

        url_prefix = detail_url_info.get('prefix')
        if url_prefix:
            url = url_prefix + url

        return url

    def get_attribute(self, instance):
        request = self.context['request']
        url_info = resolve(request.path_info)

        if self.url_kwargs:
            url_info.kwargs.update(self.url_kwargs)

        try:
            return self.get_path(instance, url_info)
        except NoReverseMatch:
            return None


class AttachmentFileField(CharField):
    def get_attribute(self, instance):
        _, filename = os.path.split(instance.file.name)

        file_url = os.path.join(
            settings.SECURE_MEDIA_URL,
            instance.signer.sign(instance.pk),
            filename
        )

        if self.context:
            context_request = self.context.get('request', None)
            if context_request:
                file_url = context_request.build_absolute_uri(file_url)

        return file_url


class Base64ImageField(CharField):
    def __init__(self, source_attr, **kwargs):
        super().__init__(**kwargs)

        self.source_attr = source_attr

    def get_attribute(self, instance):
        source = getattr(instance, self.source_attr)
        if not (isinstance(source, ImageFieldFile) and source.name):
            return None

        try:
            image_path = source.file.name
            with open(image_path, 'rb') as fp:
                mimetype = mimetype_for_file(image_path)
                prefix = 'data:{};base64,'.format(mimetype)
                base64_image = base64.b64encode(fp.read())
                return prefix + str(base64_image, 'utf-8')
        except FileNotFoundError:
            return None
