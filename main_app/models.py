# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import AbstractUser
from banksServer.settings import AUTH_USER_MODEL
from django.contrib.postgres.fields import JSONField
#from django.forms import ModelForm


# Create your models here.

# class Log(models.Model):
#     type = models.TextField()
#     text = models.TextField()

class Message(models.Model):
    name = models.CharField('Имя', max_length=20)
    phone_or_email = models.CharField('Email or Phone', max_length=100)
    message = models.TextField('Message', max_length=2000)

    class Meta:
        ordering = ['name']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return 'Message ' + str(self.name)


class User(AbstractUser):
    phone = models.CharField('Телефон', max_length=20, blank=True)
    photo = models.ImageField('Фото', max_length=100, upload_to='users_photo', blank=True, null=True)
    money = models.FloatField('Сумма', default=0)
    id_ref = models.CharField('Реферальное id', max_length=10, null=True, default=None)
    ref_procent = models.FloatField('Процент с рефералов', blank=False, null=False, default=0.15)
    valute = models.CharField('Валюта', max_length=3, default='')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class InviteRef(models.Model):
    ref_user_id = models.OneToOneField(AUTH_USER_MODEL, related_name='refuser', on_delete=models.CASCADE)
    user_id = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Реферал'
        verbose_name_plural = 'Рефералы'


class Transaction(models.Model):
    ADD = 'ADD'
    CONCLUSION = 'CON'
    REFERAL = 'REF'

    TYPE_TRANSACTION = (
        (ADD, 'Пополнить счет'),
        (CONCLUSION, 'Вывод средств'),
        (REFERAL, 'Реферальная программа')
    )

    date = models.DateTimeField('Дата', auto_now_add=True)
    type = models.CharField('Тип транзакции', max_length=3, choices=TYPE_TRANSACTION, default=ADD)
    money = models.FloatField('Сумма')
    user_id = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['date']
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'


class ChangePassword(models.Model):
    user_id = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='change_password')
    key = models.CharField('Ключ', max_length=96)
    create_time = models.DateTimeField('Время создания', auto_now=True)

    class Meta:
        ordering = ['user_id']
        verbose_name = 'Смена пароля'
        verbose_name_plural = 'Смена паролей'


class Bank(models.Model):
    country = models.CharField('Страна', max_length=20)
    name = models.CharField('Название', max_length=100)
    address = models.CharField('Адрес', max_length=200)
    phone = models.CharField('Телефон', max_length=100)
    site = models.CharField('Сайт', max_length=200)
    image = models.ImageField('Картинка', upload_to='banks_images', blank=True)
    ignore = models.BooleanField('Игнорировать', default=False)

    class Meta:
        ordering = ['country']
        verbose_name = 'Банк'
        verbose_name_plural = 'Банки'

    def __str__(self):
        return self.name + ', ' + self.country


class Route(models.Model):
    procent_profit = models.FloatField('Процент прибыли', blank=False, null=False, default=0)
    money = models.FloatField('Прибыль', blank=False, null=False, default=0)
    start_valute = models.CharField('Начальная валюта', max_length=3, blank=False, null=False)
    date = models.DateTimeField('Время получения', auto_now_add=True)
    user_id = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    route_profit = JSONField('Маршрут')
    is_accept = models.BooleanField('Допущено к выводу', default=False)

    class Meta:
        ordering = ['procent_profit']
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'


class DataReferal(models.Model):
    profit_from_friends = models.FloatField('Прибыль от друзей', blank=False, null=False, default=0)
    contrib_friends = models.FloatField('Взнос друзей', blank=False, null=False, default=0)
    profit_in_wait = models.FloatField('Прибыль от друзей в ожидании', blank=False, null=False, default=0)
    user_id = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='datareferal')

    class Meta:
        ordering = ['profit_from_friends']
        verbose_name = 'Данные по рефреалу'
        verbose_name_plural = 'Данные по рефреалам'



#Модель для теста капчи
# class MessageForm(ModelForm):
#     class Meta:
#         model = Message
#         fields = ['message']