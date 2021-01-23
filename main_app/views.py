from django.shortcuts import render
from django.views.generic import TemplateView, FormView
import json
#from main_app.models import MessageForm

# Create your views here.

from .models import Bank

def banks(request, country):
    #request.POST['country']
    # banksCountry = Bank.objects.filter(country=country).order_by('name')
    # banks = []
    # for bank in banksCountry:
    #     banks.append({'nameBank': bank.name})
    return render(request, 'first_pages/banksPage.html', None)#{'banksCountry': json.dumps(banks, ensure_ascii=False)})

def first(request):
    return render(request, 'first_pages/firstPage.html', None)

def login(request):
    return render(request, 'first_pages/loginPage.html', None)

# class IndexView(FormView):
#     template_name = 'index.html'
#     form_class = MessageForm
#
#     def form_valid(self, form):
#         # проверка валидности reCAPTCHA
#         if self.request.recaptcha_is_valid:
#             form.save()
#             return render(self.request, self.template_name, self.get_context_data())
#         return render(self.request, self.template_name, self.get_context_data())
