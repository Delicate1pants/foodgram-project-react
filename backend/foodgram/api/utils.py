import os

from django.conf import settings


def get_media_recipes_names():
    """Для кастомного поля image в RecipeSerializer"""
    dir_path = os.path.join(settings.MEDIA_ROOT, 'recipes/images/')
    return os.listdir(dir_path)
