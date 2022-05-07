from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        ]

        read_only_fields = ['id']

        # По неизвестным причинам, если написать текст ошибки blank в модели,
        # то он игнорируется и выдаётся дефолтный.
        # Поэтому пишу его здесь
        extra_kwargs = {
            'username': {
                'error_messages': {'blank': 'Обязательное поле.'}
            },
            'email': {
                'error_messages': {'blank': 'Обязательное поле.'}
            },
            'first_name': {
                'error_messages': {'blank': 'Обязательное поле.'}
            },
            'last_name': {
                'error_messages': {'blank': 'Обязательное поле.'}
            },
            'password': {
                'write_only': True,
                'error_messages': {'blank': 'Обязательное поле.'}
            },
        }
