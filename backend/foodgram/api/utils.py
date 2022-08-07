import os

from django.conf import settings

from recipes.models import IngredientAmount


def get_media_recipes_names():
    """Для кастомного поля image в RecipeSerializer"""
    dir_path = os.path.join(settings.MEDIA_ROOT, 'recipes/images/')
    return os.listdir(dir_path)


def ingr_amount_bulk_create_plus(ingredients, recipe):
    """Для кастомных методов create и update в RecipeSerializer"""
    ingredient_amounts = []
    for ingr in ingredients:
        ingredient_amounts.append(
            IngredientAmount(
                ingredient=ingr['ingredient'],
                amount=ingr['amount']
            )
        )
    IngredientAmount.objects.bulk_create(ingredient_amounts)

    recipe.ingredients.set(ingredient_amounts)

    return recipe
