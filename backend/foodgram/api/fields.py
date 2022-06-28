import base64
import binascii

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
# from django.conf import settings
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
# from dotenv import load_dotenv
from drf_extra_fields.fields import Base64FieldMixin, Base64ImageField
from rest_framework import serializers

from api.utils import get_media_recipes_names
from recipes.models import Ingredient, Tag

# import os

# from rest_framework.settings import api_settings

# load_dotenv()


class IngredientsJSONField(serializers.JSONField):
    def to_representation(self, ingredients):
        result = []
        for ingredient in ingredients:
            # try не ставлю, т.к validate_ingredients
            # проверяет существование ингредиента
            ingr_queryset = Ingredient.objects.get(
                id=ingredient['id']
            )
            ingr_dict = model_to_dict(ingr_queryset)
            ingr_dict['amount'] = ingredient['amount']
            result.append(ingr_dict)

        return result


class TagsPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, tag):
        if self.pk_field is not None:
            return self.pk_field.to_representation(tag.pk)

        tag_queryset = Tag.objects.get(
            id=tag.id
        )
        tag_dict = model_to_dict(tag_queryset)

        return tag_dict


class CustomBase64ImageField(Base64ImageField):
    def to_internal_value(self, base64_data):
        if base64_data in self.EMPTY_VALUES:
            return None

        if isinstance(base64_data, str):
            file_mime_type = None

            if ";base64," in base64_data:
                header, base64_data = base64_data.split(";base64,")
                if self.trust_provided_content_type:
                    file_mime_type = header.replace("data:", "")

            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            # Мой код ниже. Идея: генерировать имя, только если введённое имя
            # уже занято другим файлом. Иначе использовать введённое имя,
            # как указано в ТЗ

            # data может быть отрезана условием выше (if self.trust...)
            # а может и не быть
            if header.startswith('data:'):
                parse_start = header.index(':') + 1
                parse_end = header.index('/')
                file_name = header[parse_start:parse_end]
            else:
                parse_end = header.index('/')
                file_name = header[:parse_end]

            media_recipes_names = get_media_recipes_names()
            if file_name in media_recipes_names:
                file_name = self.get_file_name(decoded_file)
            # Конец моего кода.
            # Остальное скопировано у родителя Base64ImageField
            file_extension = self.get_file_extension(file_name, decoded_file)

            if file_extension not in self.ALLOWED_TYPES:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)

            complete_file_name = file_name + "." + file_extension
            data = SimpleUploadedFile(
                name=complete_file_name,
                content=decoded_file,
                content_type=file_mime_type
            )

            return super(Base64FieldMixin, self).to_internal_value(data)

        raise ValidationError(
            _("Invalid type. This is not an base64 string: {}".format(
                type(base64_data)))
        )


# class RecipeImageField(serializers.ImageField):

#     def to_internal_value(self, data):
#         data_type = str(type(data))
#         return data_type.encode('utf-8')
#         name_parse_start = data.index(':') + 1
#         name_parse_end = data.index(';')

#         img_name = data[name_parse_start:name_parse_end]
#         img_name = img_name.replace('/', '.')
#         recipes_images_path = '\\recipes\\images\\'
#         write_path = (
#             settings.MEDIA_ROOT + recipes_images_path + f'{img_name}'
#         )

#         data_parse_start = data.index(',') + 1
#         img_data = data[data_parse_start:]
#         img_data = img_data.encode('utf-8')

#         with open(f'{write_path}', 'wb') as file:
#             file.write(base64.decodebytes(img_data))

#         recipes_images_path = recipes_images_path.replace('\\', '/')
#         read_path = (
#             'http://' + os.getenv('DB_HOST') + f'{recipes_images_path}'
#             + f'{img_name}'
#         )
#         return read_path.encode('utf-8')

#         return data.encode('utf-8')

#         file_object = super().to_internal_value(data)
#         django_field = self._DjangoImageField()
#         django_field.error_messages = self.error_messages
#         return django_field.clean(file_object)

#     def to_representation(self, value):
#         # return value

#         # return str(type(value))
#         value = value.decode('utf-8')

#         if not value:
#             return None

#         use_url = getattr(
#             self, 'use_url', api_settings.UPLOADED_FILES_USE_URL
#         )
#         if use_url:
#             try:
#                 url = value.url
#             except AttributeError:
#                 return None
#             request = self.context.get('request', None)
#             if request is not None:
#                 return request.build_absolute_uri(url)
#             return url

#         return value.name
