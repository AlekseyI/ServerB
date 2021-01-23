# -*- coding: utf-8 -*-

from rest_framework import serializers
from main_app.models import *
from cryptography.fernet import Fernet
from rest_framework import exceptions
from django.contrib.auth import authenticate
import hashlib
from django.db.utils import IntegrityError
import banksServer.settings as setting
from rest_framework.authtoken.models import Token
import datetime
import requests
import banksServer.settings as Setting
from uuid import uuid4
from rest_framework.pagination import PageNumberPagination
from django.db.models import Max, Avg
import json
from .errors_manager import ErrorDescription, ErrorDescriptionField


class UserRoutesPagination(PageNumberPagination):
    page_size = 2


class TransactionPagination(PageNumberPagination):
    page_size = 5


class Captcha:

    def Validate(self, request):
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': Setting.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post(Setting.GOOGLE_RECAPTCHA_API, data=data)
        result = r.json()
        return result['success']


class Hasher():
    def __init__(self):
        self.Salt = None

    def generate_salt(self):
        self.Salt = bytes.decode(Fernet.generate_key()[:10], 'utf-8')
        return self.Salt

    def hash(self, data, salt):
        hash_pass = hashlib.sha384(str.encode(data + salt))
        return hash_pass.hexdigest()


class BankSerializer(serializers.ModelSerializer):

    @staticmethod
    def get_countries():
        return Bank.objects.values('country', 'image').distinct()

    def get_banks_country(self):
        return {'country': self.validated_data['country'],
                'banks': Bank.objects.filter(country=self.validated_data['country']).values('name')}

    class Meta:
        model = Bank
        fields = [
            'country'
        ]
        extra_kwargs = {'country': {'required': True}}


class TokenSerializer(serializers.ModelSerializer):

    # @staticmethod
    # def create_new_token(user):
    #     Token.objects.filter(user=user).delete()
    #     return Token.objects.get_or_create(user=user)

    @staticmethod
    def get_token(user):
        return Token.objects.get_or_create(user=user)

    class Meta:
        model = Token
        fields = [
            'key'
        ]


class PersonalDataSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(max_length=30, allow_blank=True, required=False)
    last_password = serializers.CharField(max_length=30, allow_blank=True, required=False)
    new_password = serializers.CharField(max_length=30, allow_blank=True, required=False)

    # def create(self, validated_data):
    #     return Token.objects.get(key=validated_data.get('token')).user

    def update(self, instance, validated_data):
        # if 'GET' in self.context:
        #     return instance
        desc_error = ErrorDescription()
        desc_error_feild = ErrorDescriptionField()
        update_password = False
        errors = []
        repeat_password = validated_data.get('repeat_password')
        last_password = validated_data.get('last_password')
        new_password = validated_data.get('new_password')

        if last_password is not None and new_password is not None and repeat_password is not None and \
                (last_password != '' or new_password != '' or repeat_password != ''):
            update_password = True

        if update_password:

            if last_password == '':
                errors.append({'last_password': [desc_error_feild.get_error(desc_error_feild.blank)]})
            if new_password == '':
                errors.append({'new_password': [desc_error_feild.get_error(desc_error_feild.blank)]})
            if repeat_password == '':
                errors.append({'repeat_password': [desc_error_feild.get_error(desc_error_feild.blank)]})

            if not instance.check_password(last_password):
                errors.append({'detail': [desc_error.last_password_invalid()]})
            if instance.check_password(new_password):
                errors.append({'detail': [desc_error.new_last_password_must_differents()]})
            if new_password != repeat_password:
                errors.append({'detail': [desc_error.new_repeat_password_not_match()]})

            if len(errors) > 0:
                raise exceptions.ValidationError(errors)

            instance.set_password(new_password)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('email', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        if 'photo' in validated_data:
            self.ChangePhoto(instance, validated_data.get('photo'))
        instance.save()
        return instance

    def ChangePhoto(self, user, new_photo):
        user.photo.delete()
        file_arr = new_photo.name.split('.')
        new_photo.name = user.id_ref + '.' + file_arr[1]
        user.photo = new_photo

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'repeat_password',
            'last_password',
            'new_password',
            'photo',
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    ref = serializers.CharField(max_length=10, allow_null=True, required=False)
    reg_password = serializers.CharField(max_length=30, min_length=8, allow_blank=False, allow_null=False,
                                         required=True, write_only=True)
    reg_repeat_password = serializers.CharField(max_length=30, min_length=8, allow_blank=False, allow_null=False,
                                                required=True, write_only=True)

    def create(self, validated_data):
        desc_error = ErrorDescription()
        try:
            user = User(email=validated_data['email'], username=validated_data['email'])
            if 'ref' in validated_data:
                try:
                    user_invited = User.objects.get(id_ref=validated_data['ref'])
                except User.DoesNotExist:
                    raise exceptions.ValidationError({'detail': [desc_error.ref_id_not_found()]})
            reg_password = validated_data['reg_password']
            reg_repeat_password = validated_data['reg_repeat_password']
            if reg_password != reg_repeat_password:
                raise exceptions.ValidationError({'detail': [desc_error.password_and_repeat_password_not_match()]})
            user.set_password(reg_password)
            user.id_ref = uuid4().hex[:10]
            user.save()
            DataReferal.objects.create(user_id=user)
            if 'ref' in validated_data:
                InviteRef.objects.create(ref_user_id=user, user_id=user_invited)

            # send_mail('Регистрация',
            #           'Вы успешно зарегистрировались',
            #           setting.EMAIL_HOST_USER,
            #           [self.validated_data['email']],
            #           fail_silently=True)
        except IntegrityError:
            raise exceptions.ValidationError({'detail': [desc_error.email_already_exists(user.email)]})
        return user

    class Meta:
        model = User
        fields = [
            'email',
            'reg_password',
            'reg_repeat_password',
            'ref'
        ]

        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False}
        }


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'name',
            'phone_or_email',
            'message'
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    password = serializers.CharField(required=True, min_length=8, max_length=30)

    def validate(self, attrs):
        desc_error = ErrorDescription()
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = authenticate(username=email, password=password)
        if user:
            if user.is_active:
                attrs['user'] = user
            else:
                raise exceptions.ValidationError({'detail': [desc_error.account_not_active()]})
        else:
            raise exceptions.ValidationError({'detail': [desc_error.invalid_email_or_password()]})
        return attrs


class ChangePasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True, allow_null=False, allow_blank=False, write_only=True)
    # должен быть еще получен url сайта
    def create(self, validated_data):
        desc_error = ErrorDescription()
        try:
            user = User.objects.get(email=validated_data['email'])
        except User.DoesNotExist:
            raise exceptions.ValidationError({'detail': [desc_error.user_with_this_email_not_found()]})
        try:
            key_pass = ChangePassword.objects.get(user_id=user)
        except ChangePassword.DoesNotExist:
            key_pass = ChangePassword(user_id=user)
        hasher = Hasher()
        key_pass.key = hasher.hash(user.email, str(datetime.datetime.now()))
        key_pass.save()
        # send_mail('Смена пароля', 'Перейдите по ссылке, чтобы изменить пароль ' +
        #           self.context['request'].build_absolute_uri().replace('change', 'new') +
        #           '?key=' + key_pass.key,
        #           setting.EMAIL_HOST_USER,
        #           [user.email],
        #           fail_silently=True)
        return key_pass

    class Meta:
        model = ChangePassword
        fields = [
            'key',
            'email'
        ]
        extra_kwargs = {'key': {'required': False}}


class CheckKeySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        desc_error = ErrorDescription()
        try:
            key_pass = ChangePassword.objects.get(key=validated_data['key'])
            if datetime.datetime.now() - key_pass.create_time > datetime.timedelta(
                    seconds=setting.TIME_LIFE_URL_CHANGE_PASSWORD):
                key_pass.delete()
                raise ChangePassword.DoesNotExist()
        except ChangePassword.DoesNotExist:
            raise exceptions.ValidationError({'detail': [desc_error.link_not_valid()]})
        return key_pass

    class Meta:
        model = ChangePassword
        fields = [
            'key'
        ]


class NewPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=30, min_length=8, required=True, allow_blank=False, allow_null=False,
                                         write_only=True)
    repeat_password = serializers.CharField(max_length=30, min_length=8, required=True, allow_blank=False, allow_null=False,
                                            write_only=True)

    def create(self, validated_data):
        desc_error = ErrorDescription()
        if validated_data['new_password'] != validated_data['repeat_password']:
            raise exceptions.ValidationError({'detail': [desc_error.new_repeat_password_not_match()]})
        try:
            key_pass = ChangePassword.objects.get(key=validated_data['key'])
        except ChangePassword.DoesNotExist:
            raise exceptions.ValidationError({'detail': [desc_error.link_not_valid()]})
        user = key_pass.user_id
        user.set_password(validated_data['new_password'])
        user.save()
        # send_mail('Пароль изменен', 'Пароль успешно изменен',
        #           setting.EMAIL_HOST_USER,
        #           [user.email],
        #           fail_silently=True)
        key_pass.delete()
        return key_pass

    class Meta:
        model = ChangePassword
        fields = [
            'key',
            'new_password',
            'repeat_password'
        ]


class DataRoutesAcceptSerializer(serializers.Serializer):
    data = serializers.JSONField(allow_null=False, required=True, write_only=True)

    # маршрут на главной обновляется каждый раз когда маршруты приходят
    def create(self, validated_data):
        data = validated_data['data']
        user_money = {}
        user_ref_minus_money = {}
        routes_today = Route.objects.filter(pk__in=data['id_routes'])
        if not data['accept']:
            for route in routes_today:
                route.delete()
            return 'Маршруты удалены'
        else:
            for route in routes_today:
                route.is_accept = True
                route.save()
                user_money[route.user_id.id] = route.money
        procent = routes_today.aggregate(Max('procent_profit'))['procent_profit__max']
        route = routes_today.filter(procent_profit=procent).order_by('-date').first()
        new_route = Route.objects.create(procent_profit=route.procent_profit,
                                         start_valute=route.start_valute,
                                         money=0,
                                         is_accept=True,
                                         route_profit=route.route_profit)
        money = 1000
        sumElemMoney = 0
        for elemRoute in new_route.route_profit:
            elemRoute['money'] = money * elemRoute['percentProfit'] / 100
            # money += elemRoute['money']
            sumElemMoney += elemRoute['money']
        new_route.money = sumElemMoney
        new_route.save()

        users = User.objects.all()

        # Здесь должен учитываться момент, что у рефрералов может быть открыт счет в другой валюте
        # и необходимо будет конвертировать в валюту пользователя
        for user in users:
            all_ref = user.inviteref_set.all()
            profit = 0
            contrib = 0
            for ref in all_ref:
                last_route = ref.ref_user_id.route_set.all().order_by('-date').first()
                user_ref_minus_money[ref.ref_user_id.id] = last_route.money * user.ref_procent / 100
                profit += last_route.money * user.ref_procent / 100
                contrib += ref.ref_user_id.money
            data_ref = user.datareferal
            data_ref.count_friends = len(all_ref)
            data_ref.profit_from_friends = profit
            data_ref.contrib_friends = contrib
            data_ref.save()
            if len(all_ref) > 0:
                user_transaction = Transaction.objects.create(type=Transaction.REFERAL,
                                                              money=profit,
                                                              user_id=user)
                user_transaction.save()

        # Обновление данных и добавление процента прибыли от рефералов
        for user in users:
            if user.id in user_ref_minus_money:
                get_money = user_money[user.id] - user_ref_minus_money[user.id]
            else:
                get_money = user_money[user.id]
            user.money += user.datareferal.profit_from_friends + get_money
            user.save()
            user_transaction = Transaction.objects.create(type=Transaction.ADD,
                                                          money=get_money,
                                                          user_id=user)
            user_transaction.save()
        return 'Маршруты успешно применены'


class DataRoutesNotAcceptSerializer(serializers.Serializer):
    data = serializers.JSONField(allow_null=False, required=True, write_only=True)

    # маршрут на главной обновляется каждый раз когда маршруты приходят
    def create(self, validated_data):
        desc_error = ErrorDescription()
        data = validated_data['data']
        data_route = None
        get_routes_id = []
        user_money = {}
        errors_valutes = ''
        if len(data) == 0:
            raise exceptions.ValidationError({'detail': [desc_error.no_routes()]})
        for routes in data:
            usersForValute = User.objects.filter(valute=routes['startValute'])
            if len(usersForValute) == 0:
                if errors_valutes != '':
                    errors_valutes += ', '
                errors_valutes += routes['startValute']
            for user in usersForValute:
                money = user.money
                sumElemMoney = 0
                for elemRoute in routes['route']:
                    elemRoute['money'] = money * elemRoute['percentProfit'] / 100
                    # money += elemRoute['money']
                    sumElemMoney += elemRoute['money']
                routes['money'] = sumElemMoney
                data_route = Route.objects.create(procent_profit=routes['percentProfit'],
                                                  start_valute=routes['startValute'],
                                                  money=routes['money'],
                                                  route_profit=routes['route'],
                                                  user_id=user)
                user_money[user.id] = sumElemMoney
                # user.money += sumElemMoney
                # user.save()
                data_route.save()
                get_routes_id.append(data_route.id)
        if data_route is None:
            raise exceptions.ValidationError({'detail': [desc_error.routes_not_recorded(errors_valutes)]})

        users = User.objects.all()

        # Здесь должен учитываться момент, что у рефрералов может быть открыт счет в другой валюте
        # и необходимо будет конвертировать в валюту пользователя
        for user in users:
            all_ref = user.inviteref_set.all()
            profit = 0
            for ref in all_ref:
                last_route = ref.ref_user_id.route_set.all().order_by('-date').first()
                profit += last_route.money * user.ref_procent / 100
            data_ref = user.datareferal
            data_ref.profit_in_wait = profit
            data_ref.save()

        self.context['id_routes'] = json.dumps(get_routes_id)

        return errors_valutes


class ReferalProgramSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    count_friends = serializers.SerializerMethodField(read_only=True)

    def get_count_friends(self, obj):
        return len(obj.user_id.inviteref_set.all())

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri().replace('referal_program', 'registration') + \
               '?ref=' + obj.user_id.id_ref

    class Meta:
        model = DataReferal
        fields = [
            'url',
            'count_friends',
            'profit_from_friends',
            'contrib_friends',
        ]


class MainPageRoutesSerializer(serializers.ModelSerializer):
    this_date = serializers.DateField(required=False, allow_null=False)
    procent_avg = serializers.SerializerMethodField(read_only=False)

    def get_procent_avg(self, obj):
        return Route.objects.filter(user_id=None, is_accept=True).aggregate(Avg('procent_profit'))[
            'procent_profit__avg']

    def create(self, validated_data):
        routes = Route.objects.filter(user_id=None, is_accept=True)
        if 'this_date' in validated_data:
            this_date = validated_data['this_date']
            try:
                route = routes.filter(date__year=this_date.year,
                                      date__month=this_date.month,
                                      date__day=this_date.day).order_by('-date').first()
            except Route.DoesNotExist:
                route = routes.order_by('-date').first()
        else:
            route = routes.order_by('-date').first()

        return route if route is not None else -1

    class Meta:
        model = Route
        fields = [
            'procent_avg',
            'procent_profit',
            'money',
            'start_valute',
            'this_date',
            'route_profit'
        ]

        extra_kwargs = {
            'start_valute': {'read_only': True},
            'route_profit': {'read_only': True},
            'money': {'read_only': True},
            'procent_profit': {'read_only': True}
        }


class UserRoutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            'procent_profit',
            'money',
            'start_valute',
            'date',
            'route_profit'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'date',
            'type',
            'money'
        ]

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'money',
            'valute',
            'photo'
        ]