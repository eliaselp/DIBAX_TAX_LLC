from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout


from App.formularios import LoginForm,Forget_pass_emailForm,TwoFactorForm,Restore_pass_form
from App.correo import enviar_correo
from App.utils import get_tocken,validar_correo,validar_tocken_restore,validar_password


import uuid
import base64
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
                        u.verificado=False
                        u.save()
                        email_c = str(u.email).encode('utf-8')
                        email_c = base64.b64encode(email_c)
                        email_c = str(email_c.decode('utf-8'))
                        return redirect(f"../../../../../../../../../../../../dibax_admin/verificacion/{email_c}/")      
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
            return redirect("../../../../../../../../dibax_admin/home/")

class Logout(View):
    def get(self,request):
        if request.user.is_authenticated:
            logout(request)
            return redirect("../../../../../../../../../dibax_admin/")
        else:
            return redirect("../../../../../../../../dibax_admin/home/")


class forgot_pass_email(View):
    def get(self,request):
        if not request.user.is_authenticated:
            formu=Forget_pass_emailForm()
            return render(request,'admin/forgot_pass_email.html',{
                "form_mail":formu
            })
        else:
            return redirect("../../../../../../../../dibax_admin/home/")
    
    def post(self,request):
        if not request.user.is_authenticated:
            form=Forget_pass_emailForm(request.POST)
            if form.is_valid():                
                email=form.cleaned_data['email']
                if User.objects.filter(email=email).exists():
                    email = str(email).encode('utf-8')
                    email = base64.b64encode(email)
                    email = str(email.decode('utf-8'))
                    return redirect(f"../../../../../../../../dibax_admin/verificacion/{email}/")
            return render(request,"admin/forgot_pass_email.html",{
                "form_mail":form,"Alerta":"Email no válido"
            })
        else:
            return redirect("../../../../../../../../dibax_admin/home/")


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
                Asunto = "Recuperacion de Clave DIBAX TAX ADMIN"
                Mensaje = f'''
                    Estimado administrador:

                    Hemos recibido una solicitud para recuperar su clave administrativa en la plataforma 
                    digital de administración de Dibax Tax Admin. 
                    Para completar el proceso, por favor utilice el siguiente código de verificación:

                    {tocken}

                    Si no solicitó la recuperación de su clave, por favor ignore este mensaje
                '''
            else:
                Asunto = "DIBAX TAX ADMIN Alerta inicio de sesión"
                Mensaje = f'''
                    Estimado administrador:

                    Hemos recibido una solicitud de acceso a la plataforma 
                    digital de administración de Dibax Tax Admin. 
                    Para completar el proceso, por favor utilice el siguiente código de verificación:

                    {tocken}

                    Si no solicitó la recuperación de su clave, por favor ignore este mensaje
                '''
            print(tocken)
            u=User.objects.get(email=email)
            u.tocken=str(tocken)
            u.save()
            enviar_correo(email=email,asunto=Asunto,mensaje=Mensaje)
            form = TwoFactorForm()
            email_c = str(email).encode('utf-8')
            email_c = base64.b64encode(email_c)
            email_c = str(email_c.decode('utf-8'))
            return render(request,"admin/verificacion.html",{
                "email":email,'form':form,
                "action_form":f"../../../../../../../../dibax_admin/forgot_pass/{email_c}/",
                "email_c":email_c
            })
        else:
            return redirect("../../../../../../../../dibax_admin/forgot_pass/")


    def post(self,request,email):
        formu=TwoFactorForm(request.POST)
        email = email.encode('utf-8')
        email = base64.b64decode(email)
        email = str(email.decode('utf-8'))
        if formu.is_valid():
            if not validar_correo(email):
                return redirect("../../../../../../../../dibax_admin/forgot_pass/")
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
                        return redirect(f"../../../../../../../../../../../dibax_admin/restore_pass/{u.tocken}/")
                    else:
                        u.verificado=True
                        u.tocken=""
                        u.save()
                        return redirect("../../../../../../../../../dibax_admin/home/")
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
                return redirect("../../../../../../../../../dibax_admin/")
        else:
            return redirect("../../../../../../../../dibax_admin/home/")

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
                            return redirect("../../../../../../../../../../../../dibax_admin/home/")                    
                    except Exception as e:
                        print(e)
                    return redirect(f"../../../../../../../../../../../../../dibax_admin/restore_pass/{tocken}/")
            else:
                return redirect("../../../../../../../../../dibax_admin/")
        else:
            return redirect("../../../../../../../../dibax_admin/home/")






class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.verificado:
                return render(request,'admin/home_admin.html')
            else:
                email_c = str(request.user.email).encode('utf-8')
                email_c = base64.b64encode(email_c)
                email_c = str(email_c.decode('utf-8'))
                return redirect(f"../../../../../../../../../../../../dibax_admin/verificacion/{email_c}/")      
        else:
            return redirect("../../../../../../../dibax_admin/")
