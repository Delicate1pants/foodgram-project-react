import base64
import binascii

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64FieldMixin, Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import CurrentUserDefault

from api.utils import get_media_recipes_names
from recipes.models import Ingredient
from users.models import User


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


class UserToRecipesRelationField(serializers.ReadOnlyField):
    """ Для полей is_favourited и is_in_shopping_cart """

    def __init__(self, model, **kwargs):
        kwargs['read_only'] = True
        self.model = model
        super().__init__(**kwargs)

    # Функция нужна чтобы послать объект класса в to_representation
    def get_attribute(self, instance):
        return instance

    def to_representation(self, obj):
        user = self.context['request'].user
        if type(user) is AnonymousUser:
            return False

        try:
            model_instance = self.model.objects.get(user=user)
            if obj in model_instance.recipes:
                return True
            return False
        except self.model.DoesNotExist:
            return False


class AuthorDefault(CurrentUserDefault):
    def __call__(self, serializer_field):
        author_id = serializer_field.context['author_id']
        return get_object_or_404(User, id=author_id)
