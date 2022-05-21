from django.db import models

from api.validators import HexCodeValidator


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    measurement_unit = models.CharField(max_length=150)


class Tag(models.Model):
    name = models.CharField(max_length=150)
    color = models.CharField(max_length=7, validators=[HexCodeValidator])
    slug = models.SlugField(unique=True)
