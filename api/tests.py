from django.test import TestCase, Client
from api.views import *
import json
import time
import os


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             password='12345678',
                                             money='125',
                                             first_name='Frank',
                                             last_name='Gholt',
                                             valute='USD')
        self.user_not_active = User.objects.create_user(username='aaa@mail.ru',
                                                        email='aaa@mail.ru',
                                                        password='12345678',
                                                        is_active=False)
        self.desc_error_field = ErrorDescriptionField()
        self.desc_error = ErrorDescription()

    def test_get_data_main_page(self):
        data = {'email': 'asd@mail.ru', 'password': '12345678'}
        response = self.client.post('/api/login/', data)
        expected = {
            'user': {
                'first_name': 'Frank',
                'last_name': 'Gholt',
                'money': 125,
                'valute': 'USD',
                'photo': None
            },
            'banks': [],
            'route': None
        }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильные данные')

    def test_success_login_user(self):
        data = {'email': 'asd@mail.ru', 'password': '12345678'}
        response = self.client.post('/api/login/', data)
        expected = 200
        get = response.status_code
        self.assertEqual(get, expected, 'Ошибка входа, код ошибки {0}'.format(response.status_code))

    def test_empty_email_password_fields(self):
        data = {'email': '', 'password': ''}
        response = self.client.post('/api/login/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.blank)],
                    'password': [self.desc_error_field.get_error(self.desc_error_field.blank)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поля email и пароль не должны быть пустыми')

    def test_invalid_password_user(self):
        data = {'email': 'asd@mail.ru', 'password': '123456789'}
        response = self.client.post('/api/login/', data)
        expected = {'detail': [self.desc_error.invalid_email_or_password()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Ожидалась ошибка входа')

    def test_invalid_email_user(self):
        data = {'email': 'ff@mail.ru', 'password': '12345678'}
        response = self.client.post('/api/login/', data)
        expected = {'detail': [self.desc_error.invalid_email_or_password()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Ожидалась ошибка входа')

    def test_no_active_user(self):
        data = {'email': 'aaa@mail.ru', 'password': '12345678'}
        response = self.client.post('/api/login/', data)
        expected = {'detail': [self.desc_error.account_not_active()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Ожидалась ошибка входа')

    def test_csrf_session_user(self):
        data = {'email': 'asd@mail.ru', 'password': '12345678'}
        response = self.client.post('/api/login/', data)
        expected = {'csrf': True, 'session': True}
        get = {'csrf': 'csrftoken' in response.cookies,
               'session': 'sessionid' in response.cookies}
        self.assertEqual(expected['csrf'], get['csrf'], 'Не был получен csrftoken')
        self.assertEqual(expected['session'], get['session'], 'Не был получен sessionid')

    def test_email_password_required_fields(self):
        data = {}
        response = self.client.post('/api/login/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.required)],
                    'password': [self.desc_error_field.get_error(self.desc_error_field.required)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'email и пароль обязательные поля')

    def test_no_correct_email_field(self):
        data = {'email': 'asd@mail', 'password': '12345678'}
        response = self.client.post('/api/login/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.invalid, serializers.EmailField)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильный формат поля email')


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             password='12345678',
                                             id_ref='2403aa122b')
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_success_registration_user_without_ref_link(self):
        data = {'email': 'user@mail.ru', 'reg_password': '12345678',
                'reg_repeat_password': '12345678'}
        response = self.client.post('/api/registration/', data)
        expected = 201
        get = response.status_code
        self.assertEqual(get, expected, 'Ошибка регистрации, код ошибки {0}'.format(response.status_code))

    def test_fail_registration_user_already_contains_without_ref_link(self):
        data = {'email': 'asd@mail.ru', 'reg_password': '12345678',
                'reg_repeat_password': '12345678'}
        response = self.client.post('/api/registration/', data)
        expected = {'detail': [self.desc_error.email_already_exists(data['email'])]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Email уже существует')

    def test_success_registration_user_with_ref_link(self):
        data = {'email': 'user@mail.ru', 'reg_password': '12345678',
                'reg_repeat_password': '12345678', 'ref': self.user.id_ref}
        response = self.client.post('/api/registration/', data)
        expected = 201
        get = response.status_code
        self.assertEqual(get, expected, 'Ошибка регистрации, код ошибки {0}'.format(response.status_code))

    def test_fail_registration_user_invalid_ref_with_ref_link(self):
        data = {'email': 'user@mail.ru', 'reg_password': '12345678',
                'reg_repeat_password': '12345678', 'ref': 'dsafsafasg'}
        response = self.client.post('/api/registration/', data)
        expected = {'detail': [self.desc_error.ref_id_not_found()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильная реферальная ссылка')

    def test_fail_registration_user_already_contains_with_ref_link(self):
        data = {'email': 'asd@mail.ru', 'reg_password': '12345678',
                'reg_repeat_password': '12345678', 'ref': self.user.id_ref}
        response = self.client.post('/api/registration/', data)
        expected = {'detail': [self.desc_error.email_already_exists(data['email'])]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'email уже существует')

    def test_empty_email_reg_password_reg_repeat_password_fields(self):
        data = {'email': '', 'reg_password': '', 'reg_repeat_password': ''}
        response = self.client.post('/api/registration/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.blank)],
                    'reg_password': [self.desc_error_field.get_error(self.desc_error_field.blank)],
                    'reg_repeat_password': [self.desc_error_field.get_error(self.desc_error_field.blank)]
                    }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поля email, пароль и повтор пароля не должны быть пустыми')

    def test_no_equal_reg__password_reg_repeat_password_fields(self):
        data = {'email': 'aaa@mail.ru', 'reg_password': '12345678',
                'reg_repeat_password': '123456789'}
        response = self.client.post('/api/registration/', data)
        expected = {'detail': [self.desc_error.password_and_repeat_password_not_match()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Пароль и повтор пароля не совпадают')

    def test_no_correct_email_reg_password_reg_repeat_password_fields(self):
        data = {'email': 'aaa@mail', 'reg_password': '1234567',
                'reg_repeat_password': '1234567'}
        response = self.client.post('/api/registration/', data)
        min_length = {'min_length': RegistrationSerializer().get_fields()['reg_password'].min_length}
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.invalid, serializers.EmailField)],
                    'reg_password': [
                        self.desc_error_field.get_error(self.desc_error_field.min_length).format(**min_length)],
                    'reg_repeat_password': [
                        self.desc_error_field.get_error(self.desc_error_field.min_length).format(**min_length)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильный формат полей email, пароля и повтор пароля')

    def test_email_reg_password_reg_repeat_password_required_fields(self):
        data = {}
        response = self.client.post('/api/registration/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.required)],
                    'reg_password': [self.desc_error_field.get_error(self.desc_error_field.required)],
                    'reg_repeat_password': [self.desc_error_field.get_error(self.desc_error_field.required)]
                    }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поля email, пароль и повтор пароля обязательные')


class ChangePasswordTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             password='12345678')
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_email_required_field(self):
        data = {}
        response = self.client.post('/api/change_password/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.required)]
                    }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поле email обязательное')

    def test_no_empty_email_field(self):
        data = {'email': ''}
        response = self.client.post('/api/change_password/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.blank)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поле email не может быть пустым')

    def test_email_not_found(self):
        data = {'email': 'aaa@mail.ru'}
        response = self.client.post('/api/change_password/', data)
        expected = {'detail': [self.desc_error.user_with_this_email_not_found()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'email не найден')

    def test_no_correct_email_field(self):
        data = {'email': 'asd@mail'}
        response = self.client.post('/api/change_password/', data)
        expected = {'email': [self.desc_error_field.get_error(self.desc_error_field.invalid, serializers.EmailField)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильный формат поля email')

    def test_change_password_success(self):
        data = {'email': 'asd@mail.ru'}
        response = self.client.post('/api/change_password/', data)
        expected = 200
        get = response.status_code
        self.assertEqual(get, expected, 'Пароль не был изменен')


class NewPasswordTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             password='12345678')
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_get_key_required_field(self):
        data = {}
        response = self.client.get('/api/new_password/', data)
        expected = {'key': [self.desc_error_field.get_error(self.desc_error_field.required)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поле key обязательное')

    def test_get_no_empty_key_field(self):
        data = {'key': ''}
        response = self.client.get('/api/new_password/', data)
        expected = {'key': [self.desc_error_field.get_error(self.desc_error_field.blank)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поле key не должно быть пустым')

    def test_get_fail_key_time_out(self):
        last_time = setting.TIME_LIFE_URL_CHANGE_PASSWORD
        setting.TIME_LIFE_URL_CHANGE_PASSWORD = 1
        response = self.client.post('/api/change_password/', {'email': self.user.email})
        self.assertEqual(response.status_code, 200, 'Ошибка на запрос изменения пароля')

        data = {'key': self.user.change_password.key}
        time.sleep(setting.TIME_LIFE_URL_CHANGE_PASSWORD)
        response = self.client.get('/api/new_password/', data)
        expected = {'detail': [self.desc_error.link_not_valid()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        setting.TIME_LIFE_URL_CHANGE_PASSWORD = last_time
        self.assertJSONEqual(get, expected, 'Время ссылки истекло')

    def test_get_fail_key_not_valid(self):
        data = {'key': 'dsfdfgh5eyrt5y536345645gtrgretgr'}
        response = self.client.get('/api/new_password/', data)
        expected = {'detail': [self.desc_error.link_not_valid()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неверный key')

    def test_post_no_correct_key_new_password_repeat_password_fields(self):
        data = {'key': 'a' * 100, 'new_password': '1234567', 'repeat_password': '1234567'}
        response = self.client.post('/api/new_password/', data)
        max_length_key = {'max_length': NewPasswordSerializer().get_fields().get('key').max_length}
        min_length_pass = {'min_length': NewPasswordSerializer().get_fields().get('new_password').min_length}
        expected = {'key': [self.desc_error_field.get_error(self.desc_error_field.max_length).format(**max_length_key)],
                    'new_password': [self.desc_error_field.get_error(self.desc_error_field.min_length).format(
                        **min_length_pass)],
                    'repeat_password': [self.desc_error_field.get_error(self.desc_error_field.min_length).format(
                        **min_length_pass)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильный формат полей key, пароля и повтор пароля')

    def test_post_no_empty_key_new_password_repeat_password_fields(self):
        data = {'key': '', 'new_password': '', 'repeat_password': ''}
        response = self.client.post('/api/new_password/', data)
        expected = {'key': [self.desc_error_field.get_error(self.desc_error_field.blank)],
                    'new_password': [self.desc_error_field.get_error(self.desc_error_field.blank)],
                    'repeat_password': [self.desc_error_field.get_error(self.desc_error_field.blank)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильный формат полей key, пароля и повтор пароля')

    def test_post_success_change_password(self):
        response = self.client.post('/api/change_password/', {'email': self.user.email})
        self.assertEqual(response.status_code, 200, 'Ошибка на запрос изменения пароля')

        data = {'key': self.user.change_password.key, 'new_password': '1234567A', 'repeat_password': '1234567A'}
        response = self.client.post('/api/new_password/', data)
        expected = 200
        get = response.status_code
        self.assertEqual(get, expected, 'Ошибка при создании пароля')

    def test_post_fail_change_password(self):
        data = {'key': 'asd', 'new_password': '1234567A', 'repeat_password': '1234567A'}
        response = self.client.post('/api/new_password/', data)
        expected = {'detail': [self.desc_error.link_not_valid()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Ошибка при смене пароля')

    def test_post_required_key_new_password_repeat_password_fields(self):
        data = {}
        response = self.client.post('/api/new_password/', data)
        expected = {'key': [self.desc_error_field.get_error(self.desc_error_field.required)],
                    'new_password': [self.desc_error_field.get_error(self.desc_error_field.required)],
                    'repeat_password': [self.desc_error_field.get_error(self.desc_error_field.required)]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Неправильный формат полей key, '
                                            'пароля и повтор пароля')

    def test_post_no_equal_new_password_repeat_password_fields(self):
        response = self.client.post('/api/change_password/', {'email': self.user.email})
        self.assertEqual(response.status_code, 200, 'Ошибка на запрос изменения пароля')

        data = {'key': self.user.change_password.key, 'new_password': '1234567A',
                'repeat_password': '1234567B'}
        response = self.client.post('/api/new_password/', data)
        expected = {'detail': [self.desc_error.new_repeat_password_not_match()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Пароли не совпадают')


class PersonalDataTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             password='12345678',
                                             first_name='Regh',
                                             last_name='Ferol',
                                             phone='78765321',
                                             id_ref='0000000000')

        self.client.force_login(self.user)
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_fail_session_csrf_personal_data(self):
        self.client.logout()

        data = {}
        response = self.client.get('/api/personal_data/', data)
        expected = {'detail': self.desc_error.authentication_credentials_not_provided()}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Не был выполнен вход')

    def test_return_personal_data(self):
        data = {}
        response = self.client.get('/api/personal_data/', data)
        expected = {'first_name': 'Regh', 'last_name': 'Ferol', 'phone': '78765321',
                    'email': 'asd@mail.ru', 'photo': None}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Были получены неправильные данные')

    def test_update_personal_data(self):
        data = {'first_name': 'Andrew', 'last_name': 'Frag', 'phone': '111111111'}
        response = self.client.post('/api/personal_data/', data)
        expected = 200
        get = response.status_code
        self.assertEqual(get, expected, 'Данные не были обновлены')

    def test_update_email(self):
        data = {'email': 'bro@mail.ru'}
        response = self.client.post('/api/personal_data/', data)
        expected = {'detail': [self.desc_error.re_authorize()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'email не был обновлен')

        response = self.client.post('/api/login/', {'email': data['email'],
                                                    'password': '12345678'},
                                    follow=True)
        self.assertEqual(response.status_code, 200, 'Ошибка входа')

    def test_update_password(self):
        data = {'last_password': '12345678', 'new_password': '12345678A',
                'repeat_password': '12345678A'}
        response = self.client.post('/api/personal_data/', data)
        expected = 200
        get = response.status_code
        self.assertEqual(get, expected, 'Пароль не был обновлен')

    def test_update_email_password(self):
        data = {'email': 'bro@mail.ru', 'last_password': '12345678',
                'new_password': '12345678A', 'repeat_password': '12345678A'}
        response = self.client.post('/api/personal_data/', data)
        expected = {'detail': [self.desc_error.re_authorize()]}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Данные не были обновлены')

        response = self.client.post('/api/login/', {'email': data['email'],
                                                    'password': data['new_password']},
                                    follow=True)
        self.assertEqual(response.status_code, 200, 'Ошибка входа')

    def test_no_empty_last_password_field(self):
        data = {'last_password': '', 'new_password': '12345678A',
                'repeat_password': '12345678A'}
        response = self.client.post('/api/personal_data/', data)
        expected = [
            {'last_password': [self.desc_error_field.get_error(self.desc_error_field.blank)]},
            {'detail': [self.desc_error.last_password_invalid()]}
        ]
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Пароль не был обновлен')

    def test_no_empty_new_password_repeat_password_field(self):
        data = {'last_password': '12345678', 'new_password': '',
                'repeat_password': ''}
        response = self.client.post('/api/personal_data/', data)
        expected = [
            {'new_password': [self.desc_error_field.get_error(self.desc_error_field.blank)]},
            {'repeat_password': [self.desc_error_field.get_error(self.desc_error_field.blank)]}
        ]
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Пароль не был обновлен')

    def test_no_equal_new_password_repeat_password_field(self):
        data = {'last_password': '12345678', 'new_password': '12345678A',
                'repeat_password': '12345678B'}
        response = self.client.post('/api/personal_data/', data)
        expected = [
            {'detail': [self.desc_error.new_repeat_password_not_match()]}
        ]
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Пароль не был обновлен')

    def test_update_photo(self):
        # Не записывается в поле photo изображение, хотя в папку сохраняется
        with open('static/test/user_photo.jpg', 'rb') as photo:
            response = self.client.post('/api/personal_data/', {'photo': photo},
                                        format='multipart')
        expected = 200
        get = response.status_code
        photo = User._meta.get_field('photo')
        media = setting.MEDIA_URL[1:]
        os.remove(media + photo.upload_to + '/' + self.user.id_ref + '.jpg')
        self.assertEqual(get, expected, 'Фото не было обновлено')


class MessageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_success_send_message(self):
        data = {'name': 'Andrew', 'phone_or_email': 'asd@mail.ru', 'message': 'Hello'}

        response = self.client.post('/api/messages/', data)
        expected = 200
        get = response.status_code
        self.assertEqual(get, expected, 'Ошибка при отправке сообщения')

    def test_no_empty_name_phone_or_email_message_fields(self):
        data = {'name': '', 'phone_or_email': '', 'message': ''}

        response = self.client.post('/api/messages/', data)
        expected = {
            'name': [self.desc_error_field.get_error(self.desc_error_field.blank)],
            'phone_or_email': [self.desc_error_field.get_error(self.desc_error_field.blank)],
            'message': [self.desc_error_field.get_error(self.desc_error_field.blank)],
        }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поля не должны быть пустыми')

    def test_required_name_phone_or_email_message_fields(self):
        data = {}

        response = self.client.post('/api/messages/', data)
        expected = {
            'name': [self.desc_error_field.get_error(self.desc_error_field.required)],
            'phone_or_email': [self.desc_error_field.get_error(self.desc_error_field.required)],
            'message': [self.desc_error_field.get_error(self.desc_error_field.required)],
        }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Поля обязательные')


class LogoutTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             password='12345678')
        self.client.force_login(self.user)
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_success_logout(self):
        data = {}

        response = self.client.post('/api/logout/', data)
        expected = 200
        get = response.status_code
        self.assertEqual(get, expected, 'Ошибка при выходе')

    def test_no_auth_fail_logout(self):
        self.client.logout()
        data = {}

        response = self.client.post('/api/logout/', data)
        expected = {'detail': self.desc_error.authentication_credentials_not_provided()}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Выход без авторизации')


class TransactionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             money=110,
                                             valute='USD',
                                             password='12345678')
        self.trans = Transaction.objects.create(type=Transaction.ADD,
                                                money=10,
                                                user_id=self.user)
        self.user_no_trans = User.objects.create_user(username='asd1@mail.ru',
                                                      email='asd1@mail.ru',
                                                      money=110,
                                                      valute='USD',
                                                      password='12345678')
        self.trans.save()
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_get_data_transaction_page(self):
        self.client.force_login(self.user)
        data = {}
        response = self.client.get('/api/user_transaction/', data)

        expected = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'date': self.trans.date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                    'type': 'ADD',
                    'money': 10
                },
            ],
            'user': {
                'first_name': '',
                'last_name': '',
                'money': 110,
                'valute': 'USD',
                'photo': None
            }
        }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Данные не совпадают')

    def test_get_empty_transaction(self):
        self.client.force_login(self.user_no_trans)
        data = {}
        response = self.client.get('/api/user_transaction/', data)

        expected = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': [],
            'user': {
                'first_name': '',
                'last_name': '',
                'money': 110,
                'valute': 'USD',
                'photo': None
            }
        }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Данные не совпадают')

    def test_fail_authentication(self):
        data = {}
        response = self.client.get('/api/user_transaction/', data)
        expected = {
            'detail': self.desc_error.authentication_credentials_not_provided()
        }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Ожидалась ошибка')


class UserScoreTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd@mail.ru',
                                             email='asd@mail.ru',
                                             money=110,
                                             valute='USD',
                                             password='12345678')
        data_route = json.dumps(
            [
                {
                    'bank': 'RCB',
                    'money': 1.0,
                    'percentProfit': 1.0
                },
                {
                    'bank': 'АО \'Джей энд Ти Банк\'',
                    'money': 2.5,
                    'percentProfit': 2.5
                },
                {
                    'bank': 'АО «ТАТСОЦБАНК» ',
                    'money': 0.25,
                    'percentProfit': 0.25
                },
                {
                    'bank': 'АО «ТАТСОЦБАНК» ',
                    'money': 0.75,
                    'percentProfit': 0.75
                }
            ], ensure_ascii=False
        )
        self.route = Route.objects.create(procent_profit=10,
                                          money=10,
                                          start_valute='USD',
                                          route_profit=data_route,
                                          user_id=self.user,
                                          is_accept=True)
        self.user_no_route = User.objects.create_user(username='asd1@mail.ru',
                                                      email='asd1@mail.ru',
                                                      money=110,
                                                      valute='USD',
                                                      password='12345678')
        self.route.save()

        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_get_data_user_score_page(self):
        self.maxDiff = None
        self.client.force_login(self.user)
        data = {}
        response = self.client.get('/api/user_score/', data)
        expected = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'procent_profit': 10,
                    'money': 10,
                    'start_valute': 'USD',
                    'date': self.route.date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                    'route_profit': json.dumps([
                        {
                            'bank': 'RCB',
                            'money': 1.0,
                            'percentProfit': 1.0
                        },
                        {
                            'bank': 'АО \'Джей энд Ти Банк\'',
                            'money': 2.5,
                            'percentProfit': 2.5
                        },
                        {
                            'bank': 'АО «ТАТСОЦБАНК» ',
                            'money': 0.25,
                            'percentProfit': 0.25
                        },
                        {
                            'bank': 'АО «ТАТСОЦБАНК» ',
                            'money': 0.75,
                            'percentProfit': 0.75
                        }
                    ], ensure_ascii=False)
                }
            ],
            'user': {
                'first_name': '',
                'last_name': '',
                'money': 110,
                'valute': 'USD',
                'photo': None
            }}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Данные не совпадают')

    def test_get_empty_routes(self):
        self.client.force_login(self.user_no_route)
        data = {}
        response = self.client.get('/api/user_score/', data)
        expected = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': [],
            'user': {
                'first_name': '',
                'last_name': '',
                'money': 110,
                'valute': 'USD',
                'photo': None
            }}
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Данные не совпадают')

    def test_fail_no_authentication(self):
        data = {}
        response = self.client.get('/api/user_score/', data)
        expected = {
            'detail': self.desc_error.authentication_credentials_not_provided()
        }
        try:
            get = json.dumps(response.json(), ensure_ascii=False)
        except TypeError:
            get = json.dumps({})
        self.assertJSONEqual(get, expected, 'Ожидалась ошибка входа')


class DataRoutesNotAcceptTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd1@mail.ru',
                                             email='asd1@mail.ru',
                                             money=110,
                                             valute='USD',
                                             password='12345678')

        self.client.force_login(self.user)
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_permission_denied(self):
        data = {}
        response = self.client.post('/api/data_routes_not_accept/', data)
        expected = status.HTTP_403_FORBIDDEN
        get = response.status_code
        self.assertEqual(get, expected, 'Ожидалась ошибка доступа')


class DataRoutesAcceptTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='asd1@mail.ru',
                                             email='asd1@mail.ru',
                                             money=110,
                                             valute='USD',
                                             password='12345678')

        self.client.force_login(self.user)
        self.desc_error = ErrorDescription()
        self.desc_error_field = ErrorDescriptionField()

    def test_permission_denied(self):
        data = {}
        response = self.client.post('/api/data_routes_accept/', data)
        expected = status.HTTP_403_FORBIDDEN
        get = response.status_code
        self.assertEqual(get, expected, 'Ожидалась ошибка доступа')

# class Test1(TestCase):
#
#     def setUp(self):
#         self.desc_error = ErrorDescriptionField()
#
#     def test_1(self):
#         print(self.desc_error.get_error(self.desc_error.blank))
