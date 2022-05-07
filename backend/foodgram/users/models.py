from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'Пользователь с таким username уже существует',
        },
    )
    email = models.EmailField(
        db_index=True,
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует',
        },
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
