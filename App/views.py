from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout

from App.formularios import LoginForm
# Create your views here.


class Login(View):
    def get(self,request):
        if not request.user.is_authenticated:
            form_login = LoginForm()
            return render(request,'admin/login.html',{
                "form_login":form_login
            })
        else:
            return redirect("../../../../../../../../dibax_admin/home/")
        

    def post(self,request):
        if not request.user.is_authenticated:
            form = LoginForm(request.POST)
            if form.is_valid():
                # Extrae los datos del formulario
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                try:
                    u=authenticate(request,username=username, password=password)
                    if u is not None:
                        auth_login(request, u)
                        return redirect("../../../../../../../../../../../../dibax_admin/home/")                    
                except Exception as e:
                    pass
                return render(request,"admin/login.html",{
                    "form_login":LoginForm(),
                    "Alerta":"Nombre de usuario o contraseña incorrecta."
                })
            else:
                return render(request,"admin/login.html",{
                    "form_login":LoginForm(),
                    "Alerta":"Todos los campos son obligatorios."
                })
        else:
            return redirect("../../../../../../../../dibax_admin/home/")

class Logout(View):
    def get(self,request):
        logout(request)
        return redirect("../../../../../../../../../dibax_admin/")

class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,'admin/home_admin.html')
        else:
            return redirect("../../../../../../../dibax_admin/")
