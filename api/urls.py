#from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

# router = DefaultRouter()
# router.register(r'banks', BankViewSet)
#
#
# urlpatterns = router.urls

urlpatterns = [
    path('banks/', BankView.as_view()),
    path('personal_data/', PersonalDataView.as_view()),
    path('registration/', RegistrationView.as_view()),
    path('messages/', MessageView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('change_password/', ChangePasswordView.as_view()),
    path('new_password/', NewPasswordView.as_view()),
    path('referal_program/', ReferalProgramView.as_view()),
    path('user_score/', UserScoreView.as_view()),
    path('main_page_routes/', MainPageRoutesView.as_view()),
    path('data_routes_not_accept/', DataRoutesNotAcceptView.as_view()),
    path('data_routes_accept/', DataRoutesAcceptView.as_view()),
    path('user_transaction/', TransactionView.as_view()),
    path('main_page/', MainPageView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)