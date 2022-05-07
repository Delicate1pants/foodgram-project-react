# Generated by Django 2.2.16 on 2022-05-07 09:01

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, error_messages={'blank': 'Обязательное поле.', 'unique': 'Пользователь с таким email уже существует'}, max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(error_messages={'blank': 'Обязательное поле.'}, max_length=150),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(error_messages={'blank': 'Обязательное поле.'}, max_length=150),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(error_messages={'blank': 'Обязательное поле.'}, max_length=150),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, error_messages={'blank': 'Обязательное поле.', 'unique': 'Пользователь с таким username уже существует'}, max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()]),
        ),
    ]
