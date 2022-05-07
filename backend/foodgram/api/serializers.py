from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name'
        ]

        extra_kwargs = {
            'username': {
                'required': True,
                'error_messages': {'required': 'Обязательное поле.'}
            },
            'password': {
                'required': True,
                'error_messages': {'required': 'Обязательное поле.'}
            },
            'email': {
                'required': True,
                'error_messages': {'required': 'Обязательное поле.'}
            },
            'first_name': {
                'required': True,
                'error_messages': {'required': 'Обязательное поле.'}
            },
            'last_name': {
                'required': True,
                'error_messages': {'required': 'Обязательное поле.'}
            }
        }
