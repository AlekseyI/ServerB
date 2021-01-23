# -*- coding: utf-8 -*-
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication,  TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import login, logout
from .serializers import *


class SessionAuthenticationWithNoCSRF(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class BankView(APIView):
    permission_classes = ()

    # отправка названий всех банков на главную стр
    def get(self, request, format=None):
        # send [{"country" : "Россия", "image" : "asd/asd.jpg"}, ... ]
        data = BankSerializer.get_countries()
        return Response(data, status=status.HTTP_200_OK)

    # отправка банков с названием страны
    def post(self, request, format=None):
        # get {"country" : "Россия"}
        serializer = BankSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.get_banks_country(), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonalDataView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    parser_classes = (MultiPartParser, FormParser,)

    # send {"first_name" : "Andrew", "last_name" : "Frags", "phone" : "0777654321", "email": "asd@mail.ru",
    # "photo" : data_photo}
    def get(self, request, format=None):
        serializer = PersonalDataSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # get {"first_name" : "Andrew", "last_name" : "Frags", "phone" : "0777654321", "email": "asd@mail.ru",
    # "last_password": "123", "repeat_password": "345",
    # "new_password":"345", "photo" : data_photo}
    def post(self, request, format=None):
        desc_error = ErrorDescription()
        # if isinstance(self.request.user, AnonymousUser):
        #     logout(request)
        #     Response({'detail': ['Пользователь не найден']}, status=status.HTTP_404_NOT_FOUND)

        user = self.request.user
        last_username = user.username
        last_password = user.password

        serializer = PersonalDataSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            update_user = serializer.save()
            # если email поменялся то отправляем запрос на перелогинивание
            if last_username != update_user.username:
                logout(request)
                return Response({'detail': [desc_error.re_authorize()]}, status=status.HTTP_200_OK)
            # если пароль поменялся, то перелогиниваемся
            if last_password != update_user.password:
                serializers = LoginSerializer(data={'email': user.email, 'password': request.data['new_password']})
                serializers.is_valid(raise_exception=True)
                logout(request)
                user = serializers.validated_data['user']
                login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None)

    # get
    # {"email": "asd",
    # "reg_password": "123",
    # "reg_repeat_password": "123",
    # "g-recaptcha-response": "asdsasfdSSFSFdgegref"
    # "ref": "53dsdgA"}
    def post(self, request, format=None):
        # if not Captcha().Validate(request):
        #     return Response({'detail': ['Неверная капча']}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(None, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None)

    def post(self, request, format=None):
        # get {"name" : "Andrew", "phone_or_email" : "asd@mail.ru", "message" : "Hello"}
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(None, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    # get {"email" : "asd@mail.ru", "password" : "123"}
    def post(self, request, format=None):
        serializers = LoginSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        user = serializers.validated_data['user']
        login(request, user)
        TokenSerializer.get_token(user)

        serializer_user_data = UserDataSerializer(user)
        user_data = serializer_user_data.data
        serializer_routes = MainPageRoutesSerializer(data=request.data)
        if serializer_routes.is_valid():
            data = serializer_routes.save()
            response_data = {'user': user_data,
                             'route': None if data == -1 else serializer_routes.data,
                             'banks': BankSerializer.get_countries()}
            return Response(response_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    # get {"email": "aleks-didenko@mail.ru"}
    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(None, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewPasswordView(APIView):
    permission_classes = ()

    # get {"key": "asjdasdy7asydashdajsd"}
    def get(self, request, format=None):
        serializer = CheckKeySerializer(data=request.GET)
        if serializer.is_valid():
            serializer.save()
            return Response(None, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # get {"key" : "asjdasdy7asydashdajsd", "repeat_password": "123", "new_password":"123"}
    def post(self, request, format=None):
        serializer = NewPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DataRoutesNotAcceptView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAdminUser, IsAuthenticated)

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    # get list routes
    def post(self, request, format=None):
        desc_error = ErrorDescription()
        serializer = DataRoutesNotAcceptSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            if result == '':
                return Response({'detail': desc_error.routes_successfully_logged(),
                                 'id_routes': serializer.context['id_routes']},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': desc_error.no_currency_users_found(result),
                                 'id_routes': serializer.context['id_routes']},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DataRoutesAcceptView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAdminUser, IsAuthenticated)

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    # get {"accept": True, "id_routes": [1, 2, 3, 5, ...]}
    def post(self, request, format=None):
        serializer = DataRoutesAcceptSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({'detail': result}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReferalProgramView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    # send {
    # "url": "http://127.0.0.1:8000/api/registration/?ref=614f2d7b09",
    # "count_friends": 0,
    # "profit_from_friends": 0,
    # "contrib_friends": 0
    # }
    def post(self, request, format=None):
        serializer = ReferalProgramSerializer(self.request.user.datareferal, context={'request': request})
        serializer_user_data = UserDataSerializer(self.request.user)
        response_data = {
            'user': serializer_user_data.data,
            'referal': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


# метод get {"page": 1}
#
class UserScoreView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    serializer_class = UserRoutesSerializer
    pagination_class = UserRoutesPagination

    def get_queryset(self):
        return self.request.user.route_set.filter(is_accept=True).order_by('-date')

    def get(self, request, *args, **kwargs):
        serializer_user_data = UserDataSerializer(self.request.user)
        response = self.list(request, *args, **kwargs)
        response.data['user'] = serializer_user_data.data
        return response


class MainPageRoutesView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    # {"this_date": "12-08-2018"} or {}
    def post(self, request, format=None):
        serializer = MainPageRoutesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination

    def get_queryset(self):
        return self.request.user.transaction_set.order_by('-date')

    def get(self, request, *args, **kwargs):
        serializer_user_data = UserDataSerializer(self.request.user)
        response = self.list(request, *args, **kwargs)
        response.data['user'] = serializer_user_data.data
        return response


class MainPageView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        return Response(None, status=status.HTTP_200_OK)

    # {}
    def post(self, request, format=None):
        user_data = None

        if self.request.user.is_authenticated:
            serializer_user_data = UserDataSerializer(self.request.user)
            user_data = serializer_user_data.data
        serializer_routes = MainPageRoutesSerializer(data=request.data)
        if serializer_routes.is_valid():
            data = serializer_routes.save()
            response_data = {'user': user_data,
                             'route': None if data == -1 else serializer_routes.data,
                             'banks': BankSerializer.get_countries()}
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer_routes.errors, status=status.HTTP_400_BAD_REQUEST)
