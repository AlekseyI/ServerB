# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import *

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = [
        'country',
        'name',
        'address',
        'phone',
        'site',
        'ignore'
    ]
    list_filter = [
        'country',
    ]
    search_fields = ['country', 'name']

    actions = None

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'date',
        'type',
        'money'
    ]

    list_filter = [
        'date',
        'type',
        'money'
    ]

    search_fields = [
        'date',
        'type'
    ]

    # readonly_fields = [
    #     'id_user'
    # ]

    actions = None

@admin.register(InviteRef)
class InviteReferalsAdmin(admin.ModelAdmin):
    list_display = [
        'user_id'
    ]


    actions = None

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone_or_email',
        'message'
    ]

    list_filter = [
        'name',
        'phone_or_email'
    ]

    search_fields = [
        'name',
        'phone_or_email',
        'message'
    ]

    actions = None
