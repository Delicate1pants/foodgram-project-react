from django.contrib import admin

from .models import Subscription, User
from recipes.models import (Favourite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favourites_count'
    )
    list_filter = ('author', 'name', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


admin.site.register(Subscription)
admin.site.register(User, UserAdmin)
admin.site.register(Favourite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
