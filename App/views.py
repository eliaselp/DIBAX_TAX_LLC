from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout


from App.formularios import LoginForm,Forget_pass_emailForm,TwoFactorForm,Restore_pass_form
from App.correo import enviar_correo
from App.utils import get_tocken,validar_correo,validar_tocken_restore,validar_password,get_metadata
from App.utils import validate_phone_number,get_Servicios

from . import models

import uuid
import base64
# Create your views here.


class Login(View):
    def get(self,request):
        if not request.user.is_authenticated:
            form_login = LoginForm()
            return render(request,'admin/login.html',{
                "form_login":form_login,
            })
        else:
            if request.user.is_staff:
                return redirect("../../../../../../../../dibaz_admin/home/")
            return redirect("../../../../../../../../../../../../../../")
        

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
                        u.verificado=False
                        u.save()
                        email_c = str(u.email).encode('utf-8')
                        email_c = base64.b64encode(email_c)
                        email_c = str(email_c.decode('utf-8'))
                        return redirect(f"../../../../../../../../../../../../dibaz_admin/verificacion/{email_c}/")      
                except Exception as e:
                    print(e)
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
            return redirect("../../../../../../../../dibaz_admin/home/")

class Logout(View):
    def get(self,request):
        if request.user.is_authenticated:
            logout(request)
            return redirect("../../../../../../../../../dibaz_admin/")
        else:
            return redirect("../../../../../../../../dibaz_admin/home/")

class forgot_pass_email(View):
    def get(self,request):
        if not request.user.is_authenticated:
            formu=Forget_pass_emailForm()
            return render(request,'admin/forgot_pass_email.html',{
                "form_mail":formu
            })
        else:
            return redirect("../../../../../../../../dibaz_admin/home/")
    
    def post(self,request):
        if not request.user.is_authenticated:
            form=Forget_pass_emailForm(request.POST)
            if form.is_valid():                
                email=form.cleaned_data['email']
                if User.objects.filter(email=email).exists():
                    email = str(email).encode('utf-8')
                    email = base64.b64encode(email)
                    email = str(email.decode('utf-8'))
                    return redirect(f"../../../../../../../../dibaz_admin/verificacion/{email}/")
            return render(request,"admin/forgot_pass_email.html",{
                "form_mail":form,"Alerta":"Email no válido"
            })
        else:
            return redirect("../../../../../../../../dibaz_admin/home/")

class forgot_pass_tocken(View):
    def get(self,request,email):
        email = email.encode('utf-8')
        email = base64.b64decode(email)
        email = str(email.decode('utf-8'))
        if validar_correo(email):
            tocken=get_tocken()
            Asunto=""
            Mensaje=""
            if not request.user.is_authenticated:
                Asunto = "Recuperacion de Clave DIBAZ TAX ADMIN"
                Mensaje = f'''
                    Estimado administrador:

                    Hemos recibido una solicitud para recuperar su clave administrativa en la plataforma 
                    digital de administración de DIBAZ TAX ADMIN. 
                    Para completar el proceso, por favor utilice el siguiente código de verificación:

                    {tocken}

                    Si no solicitó la recuperación de su clave, por favor ignore este mensaje
                '''
            else:
                Asunto = "DIBAZ TAX ADMIN Alerta inicio de sesión"
                Mensaje = f'''
                    Estimado administrador:

                    Hemos recibido una solicitud de acceso a la plataforma 
                    digital de administración de DIBAZ TAX ADMIN. 
                    Para completar el proceso, por favor utilice el siguiente código de verificación:

                    {tocken}

                    Si no solicitó la recuperación de su clave, por favor ignore este mensaje
                '''
            print(tocken)
            u=User.objects.get(email=email)
            u.tocken=str(tocken)
            u.save()
            print(Asunto)
            enviar_correo(email=email,asunto=Asunto,mensaje=Mensaje)
            form = TwoFactorForm()
            email_c = str(email).encode('utf-8')
            email_c = base64.b64encode(email_c)
            email_c = str(email_c.decode('utf-8'))
            return render(request,"admin/verificacion.html",{
                "email":email,'form':form,
                "action_form":f"../../../../../../../../dibaz_admin/forgot_pass/{email_c}/",
                "email_c":email_c
            })
        else:
            return redirect("../../../../../../../../dibaz_admin/forgot_pass/")

    def post(self,request,email):
        formu=TwoFactorForm(request.POST)
        email = email.encode('utf-8')
        email = base64.b64decode(email)
        email = str(email.decode('utf-8'))
        if formu.is_valid():
            if not validar_correo(email):
                return redirect("../../../../../../../../dibaz_admin/forgot_pass/")
            try:
                nums=[]
                for i in range(1,7):
                    nums.append(int(formu.cleaned_data[f"num{i}"]))
                u=User.objects.get(email=email)
                if str(nums) == str(u.tocken):
                    if not request.user.is_authenticated:
                        encode=f"{str(nums)}{uuid.uuid4()}".encode('utf-8')
                        encode=base64.b64encode(encode)
                        encode=encode.decode('utf-8')
                        u.tocken=str(encode).strip()
                        u.save()
                        return redirect(f"../../../../../../../../../../../dibaz_admin/restore_pass/{u.tocken}/")
                    else:
                        u.verificado=True
                        u.tocken=""
                        u.save()
                        return redirect("../../../../../../../../../dibaz_admin/home/")
            except Exception as e:
                print(e)
        email_c = str(email).encode('utf-8')
        email_c = base64.b64encode(email_c)
        email_c = str(email_c.decode('utf-8'))
        return render(request,"admin/verificacion.html",{
            "email":email,'form':formu,
            "Alerta":"Tocken Inválido",
            "email_c":email_c
        })

class Restore_pass(View):
    def get(self,request,tocken):
        if not request.user.is_authenticated:
            if validar_tocken_restore(tocken=tocken):
                form=Restore_pass_form()
                return render(request,"admin/restore.html",{
                    "form":form,"tocken":tocken
                })
            else:
                return redirect("../../../../../../../../../dibaz_admin/")
        else:
            return redirect("../../../../../../../../dibaz_admin/home/")

    def post(self,request,tocken):
        if not request.user.is_authenticated:
            if validar_tocken_restore(tocken=tocken):
                form=Restore_pass_form(request.POST)
                if form.is_valid():
                    password1=form.cleaned_data['password1']
                    password2=form.cleaned_data['password2']
                    print(password1,password2)
                    v = validar_password(password1=password1,password2=password2)
                    if v != "OK":
                        return render(request,"admin/restore.html",{
                            "form":form,"tocken":tocken,"Alerta":v
                        })
                    u = User.objects.get(tocken=tocken)
                    u.set_password(password1)
                    u.save()
                    # Extrae los datos del formulario
                    username = u.username
                    try:
                        u=authenticate(request,username=username, password=password1)
                        if u is not None:
                            auth_login(request, u)
                            u.tocken=""
                            u.save()
                            return redirect("../../../../../../../../../../../../dibaz_admin/home/")                    
                    except Exception as e:
                        print(e)
                    return redirect(f"../../../../../../../../../../../../../dibaz_admin/restore_pass/{tocken}/")
            else:
                return redirect("../../../../../../../../../dibaz_admin/")
        else:
            return redirect("../../../../../../../../dibaz_admin/home/")






class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.verificado:
                meta = get_metadata(['email','direccion','telefono'])
                servicios,disponibles = get_Servicios()
                return render(request,'admin/dashboard.html',{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles
                })
            else:
                email_c = str(request.user.email).encode('utf-8')
                email_c = base64.b64encode(email_c)
                email_c = str(email_c.decode('utf-8'))
                return redirect(f"../../../../../../../../../../../../dibaz_admin/verificacion/{email_c}/")      
        else:
            return redirect("../../../../../../../dibaz_admin/")


class set_Meta(View):
    def post(self,request,tipo):
        if request.user.is_authenticated and request.user.is_staff:
            descripcion = request.POST.get('descripcion')
            if "" in [descripcion, tipo] or tipo not in ['direccion','telefono','email']:
                print("error 1")
                return redirect("../../../../../../../../../../../dibaz_admin/home/")

            if tipo == "telefono" and not validate_phone_number(descripcion)['valid']:
                return render(request,'admin/dashboard.html',{
                    'meta': get_metadata(['contactos','direccion','telefono']),
                    "Alerta":"Numero de telefono inválido"
                })
            
            if tipo == "email" and not validar_correo(descripcion,if_existe=False):
                return render(request,'admin/dashboard.html',{
                    'meta': get_metadata(['contactos','direccion','telefono']),
                    "Alerta":"Correo electronico inválido"
                })

            if models.Metadata.objects.filter(tipo=tipo).exists():
                m = models.Metadata.objects.get(tipo=tipo)
                m.descripcion = descripcion
                m.save()
            else:
                m = models.Metadata(tipo=tipo,descripcion=descripcion)
                m.save()
        return redirect("../../../../../../../../../../../../../../../dibaz_admin/")




class Remove_meta(View):
    def get(self,request,tipo):
        if request.user.is_authenticated and request.user.is_staff:
            if tipo in ['direccion','telefono','email']:
                if models.Metadata.objects.filter(tipo=tipo).exists():
                    models.Metadata.objects.get(tipo=tipo).delete()
            return redirect("../../../../../../../../../../../dibaz_admin/home/")
        return redirect("../../../../../../../../../../../../../../../dibaz_admin/")
    


class Agg_Cita(View):
    def get(self, request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
        return redirect("../../../../../../../../../../../dibaz_admin/")
    

class Estado_Servicio(View):
    def post(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            servicio = request.POST.get('servicio')
            if servicio not in ['inmigracion','impuestos','consultoria','mentoria']:
                return redirect("../../../../../../../../../../../dibaz_admin/home/")
            
            if models.Servicios.objects.filter(clase=servicio).exists():
                s = models.Servicios.objects.get(clase=servicio)
                if s.habilitado == True:
                    s.habilitado = False
                else:
                    s.habilitado = True
                s.save()
            else:
                s = models.Servicios(clase=servicio,habilitado=False)
                s.save()
            return redirect("../../../../../../../../../../../dibaz_admin/home/")
        return redirect("../../../../../../../../../../../dibaz_admin/")