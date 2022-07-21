from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from recipes.models import Recipe


class CustomCreateModelMixin(
    mixins.CreateModelMixin
):
    def create(self, request, recipe_id=None):
        serializer = self.serializer_class(
            data=request.data, context={
                'request': request, 'recipe_id': recipe_id
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data=serializer.data
        )


class CustomDestroyModelMixin(
    mixins.DestroyModelMixin
):
    def destroy(
        self, request, related_model=None, delete_error_msg=None,
        recipe_id=None
    ):
        assert related_model is not None, (
            'Задайте значение атрибуту related_model'
        )
        assert delete_error_msg is not None, (
            'Задайте значение атрибуту delete_error_msg'
        )

        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if self.related_model.objects.filter(
                user=user,
                recipe=recipe
        ).exists():
            instance = self.related_model.objects.get(
                user=user,
                recipe=recipe
            )
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        raise ValidationError(self.delete_error_msg)
