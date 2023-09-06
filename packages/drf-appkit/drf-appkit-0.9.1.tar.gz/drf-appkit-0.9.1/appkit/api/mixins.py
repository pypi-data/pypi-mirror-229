import io
import sys

from distutils.util import strtobool
from PIL import Image, ImageOps, UnidentifiedImageError

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from filedepot.mixins import FlowFileUploadMixin

from ..models import (
    Attachment,
    ImageAttachment,
    Tag,
)
from ..util import hashed_filename
from ..settings import appkit_settings
from .serializers import ImageAttachmentBulkRepositionSerializer

User = get_user_model()
get_current_site = appkit_settings.CURRENT_SITE_ACCESSOR


# ------------------------------------------------------------------------------
# ViewSet Mixins
# ------------------------------------------------------------------------------
class DocumentViewSetMixin(object):
    def get_queryset(self):
        queryset = super().get_queryset()
        current_site = get_current_site(self.request)
        return queryset.filter(site=current_site)


class ImageAttachmentViewSetMixin(object):
    @action(detail=False, methods=['patch'])
    @transaction.atomic()
    def bulk_reposition(self, request, **kwargs):
        serializer = ImageAttachmentBulkRepositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for position_index, uuid in enumerate(validated_data['image_attachment_uuids']):
            image_attachment = ImageAttachment.objects.get(uuid=uuid)
            image_attachment.position = validated_data['positions'][position_index]
            image_attachment.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AttachmentMixin(FlowFileUploadMixin):
    @action(detail=True, methods=['delete'])
    def delete_attachment(self, request, uuid, **kwargs):
        attachment = Attachment.objects.get(uuid=request.data['item_uuid'])
        attachment.delete()

        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


    @action(detail=True, methods=['get', 'post'])
    def add_attachment(self, request, uuid, **kwargs):
        result = self.handle_flow_request(request)

        response_data = {}
        if result['finished']:
            obj = self.get_object()
            flow_file = result['file']

            attachment = Attachment.objects.create(
                content_type=ContentType.objects.get_for_model(obj),
                created_by=request.user,
                object_id=obj.id,
                file=flow_file.django_file(),
                site=get_current_site(request)
            )
            obj.attachments.add(attachment)

            # An attachment has been generated from the constructed file
            # so it can safely be discarded
            flow_file.delete()

            serializer = self.get_serializer(obj)
            response_data = serializer.data

        return Response(response_data, status=result['status'])

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, uuid, **kwargs):
        image_attachment = ImageAttachment.objects.get(uuid=request.data['item_uuid'])
        image_attachment.delete()

        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_image(self, request, uuid, **kwargs):
        obj = self.get_object()
        request_params = self.get_request_params(request)

        # Distinguish if request was issued by flow.js.
        # If it was, and if it is finished, process the file.
        flow_file = None
        flow_identifier = request_params.get('flowIdentifier')
        if flow_identifier:
            result = self.handle_flow_request(request)
            if not result['finished']:
                return Response({}, status=result['status'])

            flow_file = result['file']
            image_file = flow_file.django_file()
        else:
            image_file = request.FILES['image']

        with image_file.open() as image_stream:
            # First off, verify that the uploaded file is in fact an image
            try:
                image = Image.open(image_stream)
            except UnidentifiedImageError:
                raise ValidationError('Failed to recognize the given file as an image')

            # Let the final image filename be determined as a hash the bytes
            # of the originally uploaded image file
            image_hash = hashed_filename(image_file)
            image_filename = '{}.jpg'.format(image_hash)

            # Since we're always writing out to JPEG, discard alpha channel, if any (ex: PNG images)
            if not image.mode == 'RGB':
              image = image.convert('RGB')

            # Ensure the processed image is properly oriented
            image = ImageOps.exif_transpose(image)

            # Resize the image to fit within the defined maximum dimension
            max_image_dimension = settings.MAX_IMAGE_DIMENSION
            width, height = image.size
            if width > max_image_dimension or height > max_image_dimension:
                image.thumbnail((max_image_dimension, max_image_dimension))
                width, height = image.size

            with io.BytesIO() as image_bytes:
                image.save(image_bytes, format="JPEG", quality=80, optimize=True)

                resized_image_file = InMemoryUploadedFile(
                    file=image_bytes,
                    field_name='image',
                    name=image_filename,
                    content_type='image/jpeg',
                    size=sys.getsizeof(image_bytes),
                    charset=None
                )

                # Position the newly uploaded image at the end of the collection
                image_position = 0
                if hasattr(obj, 'images'):
                    images = obj.images.all()
                    if images.count():
                        image_position = images.last().position + 1

                image_attachment = ImageAttachment.objects.create(
                    content_type=ContentType.objects.get_for_model(obj),
                    created_by=request.user,
                    height=height,
                    image=resized_image_file,
                    object_id=obj.id,
                    position=image_position,
                    width=width,
                    site=get_current_site(request)
                )

        if strtobool(request.POST.get('feature', 'false')):
            # TODO: Move this into the view for which it applies
            obj.feature_image = image_attachment
            obj.save()

        # An image attachment has been generated from the constructed file
        # so the flow_file can be safely be discarded
        if flow_file:
            flow_file.delete()

        serializer = self.get_serializer(obj)
        serialized_data = serializer.data
        serialized_data['image_attachment_uuid'] = image_attachment.uuid

        return Response(serialized_data, status=status.HTTP_201_CREATED)


# ------------------------------------------------------------------------------
class ListExportMixin(object):
    @action(detail=False, methods=['get'])
    def export(self, request, **kwargs):
        item_qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(item_qs, many=True)
        return Response(serializer.data)


# ------------------------------------------------------------------------------
class TaggableMixin(object):
    @action(detail=False, methods=['post'])
    def batch_update_tags(self, request, **kwargs):
        tag_ids = request.data['tag_ids']
        tags = Tag.objects.filter(pk__in=tag_ids)

        item_ids = request.data['item_ids']
        item_qs = self.get_queryset().filter(pk__in=item_ids)

        action = request.data['action']
        if action == 'add':
            for item in item_qs:
                item.tags.add(*tags)
        elif action == 'remove':
            for item in item_qs:
                item.tags.remove(*tags)
        else:
            raise ValueError('"{}" is an invalid action').format(action)

        serializer = self.get_serializer(item_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_tags(self, request, uuid, **kwargs):
        obj = self.get_object()

        ids_to_add = request.data.get('ids_to_add')
        if ids_to_add:
            obj.tags.add(*Tag.objects.filter(pk__in=ids_to_add))

        ids_to_remove = request.data.get('ids_to_remove')
        if ids_to_remove:
            obj.tags.remove(*Tag.objects.filter(pk__in=ids_to_remove))

        serializer = self.get_serializer(obj)
        return Response(serializer.data)
