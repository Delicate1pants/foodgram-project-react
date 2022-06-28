from django.contrib.postgres.fields import JSONField
from django.db import models

from api.validators import HexCodeValidator
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    measurement_unit = models.CharField(max_length=150)


class Tag(models.Model):
    name = models.CharField(max_length=150)
    color = models.CharField(max_length=7, validators=[HexCodeValidator])
    slug = models.SlugField(unique=True)


class Recipe(models.Model):
    ingredients = JSONField()
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
