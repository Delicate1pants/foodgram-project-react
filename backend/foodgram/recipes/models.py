from django.db import models

from api.validators import HexCodeValidator
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=150, verbose_name='name')
    measurement_unit = models.CharField(
        max_length=150, verbose_name='measurement unit'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class IngredientAmount(models.Model):
    primary_key = models.AutoField(
        primary_key=True, verbose_name='primary key'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='ingredient'
    )
    amount = models.PositiveIntegerField(verbose_name='amount')

    class Meta:
        verbose_name = 'Ingredient amount'
        verbose_name_plural = 'Ingredient amounts'


class Tag(models.Model):
    name = models.CharField(max_length=150, verbose_name='name')
    color = models.CharField(
        max_length=7, validators=[HexCodeValidator], verbose_name='color'
    )
    slug = models.SlugField(unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        IngredientAmount, verbose_name='ingredients'
    )
    tags = models.ManyToManyField(Tag, verbose_name='tags')
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='image'
    )
    name = models.CharField(max_length=200, verbose_name='name')
    text = models.TextField(verbose_name='text')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='cooking time'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='author'
    )

    @property
    def favourites_count(self):
        """
        Дополнительное поле для админки
        """
        return Favourite.objects.filter(recipe=self.id).count()

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class Favourite(models.Model):
    primary_key = models.AutoField(
        primary_key=True, verbose_name='primary key'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites_owner',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourited_recipes',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favourites'


class ShoppingCart(models.Model):
    primary_key = models.AutoField(
        primary_key=True, verbose_name='primary key'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_owner',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'Shopping cart'
        verbose_name_plural = 'Shopping carts'
