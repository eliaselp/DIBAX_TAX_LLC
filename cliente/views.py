from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as auth_login ,logout

from . import forms
from . import models
from App import utils
from App.correo import enviar_correo
from App.formularios import Forget_pass_emailForm,Restore_pass_form
import base64
import uuid
# Create your views here.


class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                if request.user.verificado == False:
                    email_c = str(request.user.email).encode('utf-8')
                    email_c = base64.b64encode(email_c)
                    email_c = str(email_c.decode('utf-8'))
                    return redirect(f"../../../../../../../../../../../../verificacion/{email_c}/")
            except Exception as e:
                print(e)
        servicios, disponibles = utils.get_Servicios()
        return render(request,'client/index.html',{
            "contact_form":forms.ContactForm(),
            "register_form":forms.Register_Form(),
            "login_form":forms.Login_Form(),
            'meta': utils.get_metadata(['email','direccion','telefono']),
            'servicios':servicios,'disponibles':disponibles
        })

class Login(View):
    def post(self,request):
        if not request.user.is_authenticated:
            form = forms.Login_Form(request.POST)
            if form.is_valid():
                # Extrae los datos del formulario
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                try:
                    u=authenticate(request,username=username, password=password)
                    if u is not None:
                        auth_login(request, u)
                        if request.user.action_verify:
                            email_c = str(u.email).encode('utf-8')
                            email_c = base64.b64encode(email_c)
                            email_c = str(email_c.decode('utf-8'))
                            request.user.verificado=False
                            request.user.save()
                            return redirect(f"../../../../../../../../../../../../verificacion/{email_c}/")
                        request.user.verificado = True
                        request.user.save()
                        return redirect("../../../../../../../../../../../../")
                except Exception as e:
                    print(e)
                return render(request,'client/index.html',{
                    "contact_form":forms.ContactForm(),
                    "register_form":forms.Register_Form(),
                    "login_form":form,
                    "Alerta":"Nombre de usuario o contraseña incorrecto"
                })
            else:
                return render(request,'client/index.html',{
                    "contact_form":forms.ContactForm(),
                    "register_form":forms.Register_Form(),
                    "login_form":form,
                    "Alerta":"Todos los campos son obligatorios."
                })
        else:
            return redirect("../../../../../../../../../../../../../")

class Logout(View):
    def get(self,request):
        if request.user.is_authenticated:
            logout(request)
        return redirect("../../../../../../../../../../../../../../")


class Register(View):
    def post(self,request):
        if not request.user.is_authenticated:
            register_form = forms.Register_Form(request.POST)
            if register_form.is_valid():
                fname=str(register_form.cleaned_data['fname']).strip().title()
                lname=str(register_form.cleaned_data['lname']).strip().title()
                username=str(register_form.cleaned_data['username']).strip()
                email=str(register_form.cleaned_data['email']).strip()
                phone=str(register_form.cleaned_data['phone']).strip()
                password1=register_form.cleaned_data['password1']
                password2=register_form.cleaned_data['password2']
                if not forms.validate_name(fname):
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":"Los nombres solo admiten letras mayúsculas, minúsculas y caracter espacio."
                    })
                if not forms.validate_name(lname):
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":"Los apellidos solo admiten letras mayúsculas, minúsculas y caracter espacio."
                    })
                if not forms.validate_username(username):
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":"El username solo admite letras mayúsculas y minúsculas y numeros."
                    })
                if User.objects.filter(username=username).exists():
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":"El username esta en uso."
                    })
                if not forms.validar_correo(email):
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":"El correo electrónico esta en uso."
                    })
                
                if models.Cliente.objects.filter(First_Name=fname,Last_Name=lname).exists():
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":"Nombres y apellidos en uso"
                    })
                if utils.validate_phone_number(phone_number=phone).get('valid')==False:
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":"Número de teléfono inválido"
                    })
                v = forms.validar_password(password1=password1,password2=password2)
                if v != "OK":
                    return render(request,'client/index.html',{
                        "contact_form":forms.ContactForm(),
                        "register_form":register_form,
                        "login_form":forms.Login_Form(),
                        "Alerta":v
                    })
                try:
                    u=User(username=username,email=email)
                    u.set_password(password1)
                    u.nuevo = True
                    u.save()
                    nc=models.Cliente(userid=u,First_Name=fname,Last_Name=lname,Phone=phone)
                    nc.save()
                    u=authenticate(request,username=username, password=password1)
                    if u is not None:
                        auth_login(request, u)
                        email_c = str(email).encode('utf-8')
                        email_c = base64.b64encode(email_c)
                        email_c = str(email_c.decode('utf-8'))
                        request.user.nuevo=True
                        request.user.verificado = False
                        request.user.action_verify = True
                        request.user.save()
                        return redirect(f"../../../../../../../../../../../../verificacion/{email_c}/")
                except Exception as e:
                    print(e)
            else:
                return render(request,'client/index.html',{
                    "contact_form":forms.ContactForm(),
                    "register_form":register_form,
                    "login_form":forms.Login_Form(),
                    "Alerta":"Todos los campos son obligatorios"
                })
        return redirect("../../../../../../../../../../../../../")


class Forget_pass_email(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return render(request,"client/forget_pass_email.html",{
                "form_mail": Forget_pass_emailForm()
            })
        return redirect("../../../../../../../../../../../../../../")
    
    def post(self,request):
        if not request.user.is_authenticated:
            form = Forget_pass_emailForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                if utils.validar_correo(email,if_existe=False):
                    if not User.objects.filter(email=email).exists():
                        return render(request,"client/forget_pass_email.html",{
                            "form_mail": form,
                            "Alerta":"Correo electronico inválido"
                        })
                    email_c = str(email).encode('utf-8')
                    email_c = base64.b64encode(email_c)
                    email_c = str(email_c.decode('utf-8'))
                    return redirect(f'../../../../../../../../../../../verificacion/{email_c}/')
                else:
                    return render(request,"client/forget_pass_email.html",{
                        "form_mail": form,
                        "Alerta":"Correo electronico inválido"
                    })
            else:
                return render(request,"client/forget_pass_email.html",{
                    "form_mail": form,
                    "Alerta":"Todos los campos son obligatorios"
                })
        return redirect("../../../../../../../../../../../../../../")



class Verificacion(View):
    def get(self,request,email):
        email = email.encode('utf-8')
        email = base64.b64decode(email)
        email = str(email.decode('utf-8'))
        if utils.validar_correo(email,if_existe=False):
            if not User.objects.filter(email=email).exists():
                return redirect("../../../../../../../../../../../../../")
            tocken=utils.get_tocken()
            Asunto = None
            Mensaje = None
            if request.user.is_authenticated:
                if request.user.nuevo == True:
                    Asunto = "Confirmación de Registro en DIBAX TAX LLC"
                    Mensaje = f'''
                        Estimado {request.user.username}:

                        Usted se ha registrado en la plataforma digital de la compañía 
                        DIBAX TAX LLC. 

                        Para completar el proceso de registro, por favor utilice el siguiente código de verificación:

                        {tocken}

                        Muchas gracias por elegirnos, será un placer atenderle.
                    '''
                elif request.user.nuevo == False:
                    Asunto = "Alerta de Inicio de sesión en DIBAX TAX LLC"
                    Mensaje = f'''
                        Estimado {request.user.username}:

                        Usted está autenticandose en la plataforma digital de la compañía 
                        DIBAX TAX LLC. 

                        Para completar el proceso de registro, por favor utilice el siguiente código de verificación:

                        {tocken}

                        Muchas gracias por elegirnos, será un placer atenderle.
                    '''
            else:
                Asunto = "Recuperacion de Clave DIBAX TAX LLC"
                Mensaje = f'''
                    Estimado {request.user.username}:

                    Hemos recibido una solicitud para recuperar su clave en la plataforma 
                    digital DIBAX TAX LLC. 
                    Para completar el proceso, por favor utilice el siguiente código de verificación:

                    {tocken}
                    
                    Si no ha sido usted ignore este mensaje y no comparta este codigo con nadie.
                    Muchas gracias por elegirnos, será un placer atenderle.
                '''
            print(tocken)
            u=User.objects.get(email=email)
            u.tocken=str(tocken)
            u.save()
            print(Asunto)
            enviar_correo(email=email,asunto=Asunto,mensaje=Mensaje)
            form = forms.TwoFactorForm()
            email_c = str(email).encode('utf-8')
            email_c = base64.b64encode(email_c)
            email_c = str(email_c.decode('utf-8'))
            return render(request,"client/verificacion.html",{
                "email":email,'form':form,
                "action_form":f"../../../../../../../../verificacion/{email_c}/"
            })


    def post(self,request,email):
        formu=forms.TwoFactorForm(request.POST)
        email = email.encode('utf-8')
        email = base64.b64decode(email)
        email = str(email.decode('utf-8'))
        if formu.is_valid():
            if not utils.validar_correo(email,if_existe=False) or not User.objects.filter(email=email).exists():
                return redirect("../../../../../../../../../../../../")
            try:
                nums=[]
                for i in range(1,7):
                    nums.append(int(formu.cleaned_data[f"num{i}"]))
                u=User.objects.get(email=email)
                if str(nums) == str(u.tocken):
                    if request.user.is_authenticated:
                        u.tocken=""
                        u.nuevo=False
                        u.verificado = True
                        u.save()
                        return redirect(f"../../../../../../../../../../../../../../")
                    else:
                        encode=f"{str(nums)}{uuid.uuid4()}".encode('utf-8')
                        encode=base64.b64encode(encode)
                        encode=encode.decode('utf-8')
                        u.tocken=str(encode).strip()
                        u.save()
                        return redirect(f"../../../../../../../../../../../restore_pass/{u.tocken}/")
            except Exception as e:
                print(e)
        return render(request,"client/verificacion.html",{
            "email":email,'form':formu,
            "Alerta":"Tocken Inválido"
        })







class Restore_pass(View):
    def get(self,request,tocken):
        if not request.user.is_authenticated:
            if utils.validar_tocken_restore(tocken=tocken):
                form=Restore_pass_form()
                return render(request,"client/restore.html",{
                    "form":form,"tocken":tocken
                })
        return redirect("../../../../../../../../../../../../../../../../../../")

    def post(self,request,tocken):
        if not request.user.is_authenticated:
            if utils.validar_tocken_restore(tocken=tocken):
                form=Restore_pass_form(request.POST)
                if form.is_valid():
                    password1=form.cleaned_data['password1']
                    password2=form.cleaned_data['password2']
                    print(password1,password2)
                    v = utils.validar_password(password1=password1,password2=password2)
                    if v != "OK":
                        return render(request,"client/restore.html",{
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
                            return redirect("../../../../../../../../../../../../../../../../../../")                    
                    except Exception as e:
                        print(e)
                    return redirect(f"../../../../../../../../../../../../../restore_pass/{tocken}/")
        return redirect("../../../../../../../../../../../../../../")




class Set_2fa(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.action_verify == True:
                request.user.action_verify = False
            else:
                request.user.action_verify = True
            request.user.save()
        return redirect("../../../../../../../../../../../../../")