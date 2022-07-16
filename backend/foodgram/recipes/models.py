from django.db import models

from api.validators import HexCodeValidator
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    measurement_unit = models.CharField(max_length=150)


class IngredientAmount(models.Model):
    primary_key = models.AutoField(primary_key=True)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.PositiveIntegerField()


class Tag(models.Model):
    name = models.CharField(max_length=150)
    color = models.CharField(max_length=7, validators=[HexCodeValidator])
    slug = models.SlugField(unique=True)


class Recipe(models.Model):
    ingredients = models.ManyToManyField(IngredientAmount)
    tags = models.ManyToManyField(Tag)
    image = models.ImageField(upload_to='recipes/images/')
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author'
    )

    @property
    def is_favourited(self):
        """
        Hook, за который будет дёргать фильтр
        """
        return None

    @property
    def is_in_shopping_cart(self):
        """
        Hook, за который будет дёргать фильтр
        """
        return None


class Favourites(models.Model):
    primary_key = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites_owner'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourited_recipes'
    )


class Shopping_cart(models.Model):
    primary_key = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_owner'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart'
    )
