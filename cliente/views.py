from django.shortcuts import render
from django.views import View
from . import forms
# Create your views here.


class Index(View):
    def get(self,request):
        return render(request,'cliente/index.html',{
            "contact_form":forms.ContactForm()
        })
