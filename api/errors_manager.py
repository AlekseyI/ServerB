from rest_framework import serializers
from banksServer import settings as setting


class ErrorDescriptionField:
    _lst_fileds = [serializers.CharField, serializers.EmailField,
                   serializers.IntegerField, serializers.ImageField,
                   serializers.JSONField, serializers.DateTimeField,
                   serializers.DateField, serializers.FloatField,
                   serializers.BooleanField]

    def __init__(self):
        self.blank = 'blank'
        self.required = 'required'
        self.invalid = 'invalid'
        self.null = 'null'
        self.max_length = 'max_length'
        self.min_length = 'min_length'
        self.max_string_length = 'max_string_length'
        self.min_value = 'min_value'
        self.max_value = 'max_value'
        self.invalid_image = 'invalid_image'
        self.empty = 'empty'
        self.no_name = 'no_name'

    def get_error(self, key_error, field=None):
        select_field = []
        if field is not None:
            select_field = [f for f in self._lst_fileds if f is field]
            if len(select_field) == 0:
                return 'Field with type: {0} not found'.format(field.__name__)

        fld = self._lst_fileds if field is None else select_field
        for f in fld:
            for k, v in f().error_messages.items():
                if k == key_error:
                    return v
        return 'Key error: {0} not found'.format(key_error)


class ErrorDescription:
    _languages = ['ru', 'en']

    def __init__(self, lang=setting.LANGUAGE_CODE):
        self.Lang = self.__select_lang(lang)

    def __select_lang(self, lang):
        for l in self._languages:
            if lang.lower().__contains__(l):
                return l

    def ref_id_not_found(self):
        m = {
            'ru': 'Реферальное id не существует',
            'en': 'Referal id not found'
        }
        return m[self.Lang]

    def last_password_invalid(self):
        m = {
            'ru': 'Старый пароль неверно введен',
            'en': 'Old password invalid'
        }
        return m[self.Lang]

    def new_last_password_must_differents(self):
        m = {
            'ru': 'Новый пароль должен отличаться от старого',
            'en': 'The new password must be different from the old one'
        }
        return m[self.Lang]

    def new_repeat_password_not_match(self):
        m = {
            'ru': 'Новый пароль и повтор пароля не совпадают',
            'en': 'New password and repeat password do not match'
        }
        return m[self.Lang]

    def password_and_repeat_password_not_match(self):
        m = {
            'ru': 'Пароли не совпадают',
            'en': 'Passwords do not match'
        }
        return m[self.Lang]

    def email_already_exists(self, email):
        m = {
            'ru': 'email: {0} уже существует',
            'en': 'email: {0} already exists'
        }
        return m[self.Lang].format(email)

    def account_not_active(self):
        m = {
            'ru': 'Аккаунт не активен',
            'en': 'Account is not active'
        }
        return m[self.Lang]

    def invalid_email_or_password(self):
        m = {
            'ru': 'Неверно введен email или пароль',
            'en': 'Invalid email or password'
        }
        return m[self.Lang]

    def user_with_this_email_not_found(self):
        m = {
            'ru': 'Пользователь с таким email не обнаружен',
            'en': 'User with this email is not found'
        }
        return m[self.Lang]

    def link_not_valid(self):
        m = {
            'ru': 'Ссылка не действительна или ее срок действия истек',
            'en': 'The link is not valid or has expired'
        }
        return m[self.Lang]

    def re_authorize(self):
        m = {
            'ru': 'Переавторизоваться',
            'en': 'Re-authorize'
        }
        return m[self.Lang]

    def authentication_credentials_not_provided(self):
        m = {
            'ru': 'Учетные данные не были предоставлены.',
            'en': 'Authentication credentials were not provided.'
        }
        return m[self.Lang]

    def invalid_header(self):
        m = {
            'ru': 'Недопустимый заголовок. Учетные данные некорректно закодированны в base64.',
            'en': 'Invalid basic header. Credentials not correctly base64 encoded.'
        }
        return m[self.Lang]

    def no_routes(self):
        m = {
            'ru': 'Нет маршрутов',
            'en': 'No routes'
        }
        return m[self.Lang]

    def no_currency_users_found(self, currencies):
        m = {
            'ru': 'Не найдены пользователи с валютами: {0}',
            'en': 'No users found with currencies: {0}'
        }
        return m[self.Lang].format(currencies)

    def routes_successfully_logged(self):
        m = {
            'ru': 'Маршруты успешно записаны',
            'en': 'Routes successfully logged'
        }
        return m[self.Lang]

    def routes_not_recorded(self, currencies):
        m = {
            'ru': 'Маршруты не были записаны, т.к. пользователи с валютами: {0}, не найдены',
            'en': 'Routes not recorded, because users with currencies: {0}, not found'
        }
        return m[self.Lang].format(currencies)

    def permission_denied(self):
        m = {
            'ru': 'У вас нет прав для выполнения этой операции.',
            'en': 'You do not have permission to perform this action.'
        }
        return m[self.Lang]
