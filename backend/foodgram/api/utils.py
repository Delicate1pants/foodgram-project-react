from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response.status_code == 400:
        for field in response.data:
            # Текст ошибки для blank в модели игнорится и используется дефолт
            # Даже в сериализаторе не всегда получается поменять этот текст
            # Поэтому делаю это здесь
            if response.data[field] == ['Это поле не может быть пустым.']:
                response.data[field] = 'Обязательное поле.'
    if response.status_code == 401:
        if response.data['detail']:
            if response.data['detail'] == 'Недопустимый токен.':
                response.data['detail'] = 'Учетные данные не были предоставлены.' # noqa E501

    return response
