from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as auth_login ,logout
from django.utils import timezone

from . import forms
from . import models
from App import utils
from App.correo import enviar_correo
from App import models as admin_models
from App.formularios import Forget_pass_emailForm,Restore_pass_form
import base64
import uuid
import bleach

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
        verificado = False
        try:
            verificado = models.Cliente.objects.get(userid=request.user).Verificado
        except Exception as e:
            pass
        return render(request,'client/index.html',{
            "register_form":forms.Register_Form(),
            "login_form":forms.Login_Form(),
            'meta': utils.get_metadata(['email','direccion','telefono']),
            'servicios':servicios,'disponibles':disponibles,
            'fechas_disponibles':utils.get_fechas_disponibles(),
            "verificado":verificado
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
                        u.ultimo_login = timezone.now()
                        u.authenticated = True
                        u.verificado = True
                        u.save()
                        if request.user.action_verify:
                            email_c = str(u.email).encode('utf-8')
                            email_c = base64.b64encode(email_c)
                            email_c = str(email_c.decode('utf-8'))
                            request.user.verificado=False
                            request.user.save()
                            return redirect(f"../../../../../../../../../../../../verificacion/{email_c}/")
                        return redirect("../../../../../../../../../../../../")
                except Exception as e:
                    print(e)
                return utils.alerta_cliente_index(request=request,Alerta="Nombre de usuario o contraseña incorrecto")
            else:
                return utils.alerta_cliente_index(request=request,Alerta="Todos los campos son obligatorios.")
        else:
            return redirect("../../../../../../../../../../../../../")

class Logout(View):
    def get(self,request):
        if request.user.is_authenticated:
            request.user.authenticated = False
            request.user.save()
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
                    return utils.alerta_cliente_index(request=request,Alerta="Los nombres solo admiten letras mayúsculas, minúsculas y caracter espacio.")
                    
                if not forms.validate_name(lname):
                    return utils.alerta_cliente_index(request=request,Alerta="Los apellidos solo admiten letras mayúsculas, minúsculas y caracter espacio.")
                    
                if not forms.validate_username(username):
                    return utils.alerta_cliente_index(request=request,Alerta="El username solo admite letras mayúsculas y minúsculas y numeros.")
                    
                if User.objects.filter(username=username).exists():
                    return utils.alerta_cliente_index(request=request,Alerta="El username esta en uso.")
                    
                if not forms.validar_correo(email):
                    return utils.alerta_cliente_index(request=request,Alerta="El correo electrónico esta en uso.")
                    
                
                if models.Cliente.objects.filter(First_Name=fname,Last_Name=lname).exists():
                    return utils.alerta_cliente_index(request=request,Alerta="Nombres y apellidos en uso")
                    
                if utils.validate_phone_number(phone_number=phone)==False:
                    return utils.alerta_cliente_index(request=request,Alerta="Número de teléfono inválido")
                    
                v = forms.validar_password(password1=password1,password2=password2)
                if v != "OK":
                    return utils.alerta_cliente_index(request=request,Alerta=v)
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
                return utils.alerta_cliente_index(request=request,Alerta="Todos los campos son obligatorios")
                
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
            if request.user.is_authenticated and not request.user.antiphishing in ["",None]:
                Mensaje += f"Código antiphishing: {request.user.antiphishing}"
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
                            u.ultimo_login = timezone.now()
                            u.authenticated = True
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
    



class Agg_Cita(View):
    def post(self, request,servicio):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return utils.alerta_cliente_index(request=request,Alerta="Registre esta cita en el panel de administración")
            cliente = None
            try:
                cliente = models.Cliente.objects.get(userid=request.user)
            except Exception as e:
                print(e)
                return utils.alerta_cliente_index(request=request,Alerta="No se pudo registrar la cita")
            if servicio not in ["inmigracion","impuestos","consultoria"]:
                return utils.alerta_cliente_index(request=request,Alerta="Servicio no valido")
            
            descripcion = request.POST.get("descripcion")
            fecha = request.POST.get("fecha")
            detalles = request.POST.get("detalles")
            

            if servicio in ["inmigracion","impuestos","consultoria"]:
                if "" in [descripcion,fecha,detalles]:
                    return utils.alerta_cliente_index(request=request,Alerta="Todos los campos son obligatorios")
                
                descripcion = bleach.clean(descripcion)
                detalles = bleach.clean(detalles)
                
                descripciones = None
                if servicio == "inmigracion":
                    descripciones = [
                        "Residencia",
                        "Peticiones Familiares",
                        "Naturalización",
                        "Cambios de Dirección",
                        "Visa Fiancé",
                        "Autorizo de Viaje",
                        "Parole Humanitario",
                        "Solicitud de Asilo",
                        "Extensión de Estadia de No Migrante",
                        "Fee Waiver",
                        "Petición FOIA",
                        "Lotería de Visas",
                        "Visas de Turismo B1/B2",
                        "Mociones en Corte",
                        "Prosecutorial Discretion",
                        "Retiro de Asilo",
                        "Reapertura de Casos USCIS",
                        "Perdones Migratorios",
                        "Estatus de Protección Temporal (TPS)",
                        "Otra",
                    ]
                    servicio = "Trámites migratorios"
                elif servicio == "impuestos":
                    descripciones = [
                        "ITIN con Certificado Forense",
                        "Texas Notary Public",
                        "Declaración de Impuestos",
                        "Formación de Compañías",
                        "Obtención de EIN",
                        "Traducción de Documentos",
                        "Ministro de Bodas",
                        "Otra"
                    ]
                    servicio = "Impuestos y Emprendimientos"
                elif servicio == "consultoria":
                    descripciones = [
                        "Pasaporte",
                        "Visa HE 11",
                        "Autorizacion de Menores",
                        "Visa de Turismo B1/B2",
                        "Poderes y Legalizaciones",
                        "Otra",
                    ]
                    servicio = "Servicios Consulares Cubanos"
                if descripcion not in descripciones:
                    return utils.alerta_cliente_index(request=request,Alerta="Descripción no válida")
                
                if not utils.validar_fecha(fecha):
                    return utils.alerta_cliente_index(request=request,Alerta="Formato de fecha no válido")
                if not utils.get_fechas_disponibles(check=fecha):
                    return utils.alerta_cliente_index(request=request,Alerta="La fecha seleccionada no esta disponible")
                nueva_cita = admin_models.Citas(
                    nombre=None,phone=None,
                    clienteid=cliente,fecha=fecha,hora=None,servicio=servicio,
                    descripcion=descripcion,detalles=detalles,importe=None,factura=None,
                    nueva=True,aprobada=False,finalizada=False
                )
                nueva_cita.save()
                return redirect("../../../../../../../../../../../../mis_citas/")
        return redirect("../../../../../../../../../../../dibaz_admin/")



class Mis_Citas(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect("../../../../../../../../../../../../../")
            servicios, disponibles = utils.get_Servicios()
            verificado = False
            cliente = None
            try:
                cliente = models.Cliente.objects.get(userid=request.user)
                verificado = cliente.Verificado
            except Exception as e:
                pass
            return render(request,'client/mis_citas.html',{
                'meta': utils.get_metadata(['email','direccion','telefono']),
                'servicios':servicios,'disponibles':disponibles,
                'fechas_disponibles':utils.get_fechas_disponibles(),
                "verificado":verificado,
                "mis_citas":admin_models.Citas.objects.filter(clienteid=cliente).order_by('-id')
            })
        return redirect("../../../../../../../../../../../../../")






class Cancelar_Cita(View):
    def post(self,request):
        if request.user.is_authenticated:
            id = request.POST.get("id")
            try:
                cita = admin_models.Citas.objects.get(id=id)
                cita.nueva = False
                cita.aprobada = False
                cita.finalizada = True
                cita.cancelada = True
                cita.save()
                return redirect("../../../../../../../../../../../../../mis_citas/")
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../../../../../")
    

class Set_antiphishing(View):
    def post(self,request):
        if request.user.is_authenticated:
            print(request.POST)
            antiphishing = str(request.POST.get("antiphishing")).strip()
            if "" == antiphishing:
                if request.POST.get("perfil") == "true":
                    return utils.alerta_cliente_perfil(request=request,Alerta="Todos los campos son obligatorios")
                return utils.alerta_cliente_index(request=request,Alerta="Todos los campos son obligatorios")
            antiphishing = bleach.clean(str(antiphishing))
            request.user.antiphishing = antiphishing
            request.user.save()
        if request.POST.get("perfil") == "true":
            return redirect("../../../../../../../../../../../../../../../../../../../perfil/")
        return redirect("../../../../../../../../../../../../../../../../../../../")


class Delete_antiphishing(View):
    def get(self,request):
        if request.user.is_authenticated:
            request.user.antiphishing = None
            request.user.save()
        return redirect("../../../../../../../../../../../../../../../../../../../")
    

class Perfil(View):
    def get(self,request):
        if request.user.is_authenticated:
            servicios, disponibles = utils.get_Servicios()
            verificado = False
            cliente = None
            try:
                cliente = models.Cliente.objects.get(userid=request.user)
                verificado = cliente.Verificado
            except Exception as e:
                pass
            return render(request,'client/perfil.html',{
                'meta': utils.get_metadata(['email','direccion','telefono']),
                'servicios':servicios,'disponibles':disponibles,
                'fechas_disponibles':utils.get_fechas_disponibles(),
                "verificado":verificado,"cliente":cliente
            })
        return redirect("../../../../../../../../../../../../../../../../../../../")
    def post(self,request):
        if request.user.is_authenticated:
            username=str(request.POST.get("username")).strip()
            email=str(request.POST.get("email")).strip()
            fname=str(request.POST.get("fname")).strip().title()
            lname=str(request.POST.get("lname")).strip().title()
            phone=str(request.POST.get("phone")).strip()

            if "" in [username,email,fname,lname,phone]:
                return utils.alerta_cliente_perfil(request=request,Alerta="Todos los campos son obligatorios")
            username = bleach.clean(username)
            email = bleach.clean(email)
            fname = bleach.clean(fname)
            lname = bleach.clean(lname)
            phone = bleach.clean(phone)
            try:
                if username!=request.user.username:
                    if not forms.validate_username(username):
                        return utils.alerta_cliente_perfil(request=request,Alerta="El nombre de usuario solo admite letras mayúsculas, minúsculas y números.")
                    if User.objects.filter(username=username).exists():
                        return utils.alerta_cliente_perfil(request=request,Alerta="El nombre de usuario esta en uso.")
                    request.user.username = username
                    request.user.save()
                if email!=request.user.email:
                    if not forms.validar_correo(email):
                        return utils.alerta_cliente_perfil(request=request,Alerta="Formato de correo electrónico incorrecto")
                    if User.objects.filter(email=email).exists():
                        return utils.alerta_cliente_perfil(request=request,Alerta="El correo electrónico esta en uso.")
                    request.user.email = email
                    request.user.save()
                cliente = models.Cliente.objects.get(userid=request.user)
                if fname!=cliente.First_Name or lname!=cliente.Last_Name:
                    if forms.validate_name(fname):
                        return utils.alerta_cliente_perfil(request=request,Alerta="El nombre solo admite letras mayúsculas, minúsculas y espacios.")
                    if forms.validate_name(lname):
                        return utils.alerta_cliente_perfil(request=request,Alerta="El apellido solo admite letras mayúsculas, minúsculas y espacios.")
                    if models.Cliente.objects.filter(First_Name=fname,Last_Name=lname):
                        return utils.alerta_cliente_perfil(request=request,Alerta="Los nombres y apellidos estan en uso.")
                    cliente.First_Name=fname
                    cliente.Last_Name=lname
                    cliente.save()
                if phone != cliente.Phone:
                    if not utils.validate_phone_number(phone_number=phone):
                        return utils.alerta_cliente_perfil(request=request,Alerta="Numero de teléfono inválido")
                    cliente.Phone = phone
                    cliente.save()
                return redirect("../../../../../../../../../../../../../../../../../../perfil/")
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../../../../../../../../../../../")




class Set_password(View):
    def post(self,request):
        if request.user.is_authenticated:
            password0 = request.POST.get("password0")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            
            if "" in [password0,password1,password2]:
                return utils.alerta_cliente_perfil(request=request,Alerta="Todos los campos son obligatorios")
            password0 = bleach.clean(password0)
            password1 = bleach.clean(password1)
            password2 = bleach.clean(password2)
            if request.user.check_password(password0):
                v = utils.validar_password(password1=password1,password2=password2)
                if v != "OK":
                    return utils.alerta_cliente_perfil(request=request,Alerta=v)
                request.user.set_password(password2)
                request.user.save()
                u=authenticate(request,username=request.user.username, password=password2)
                if u is not None:
                    auth_login(request, u)
                    u.ultimo_login = timezone.now()
                    u.authenticated = True
                    u.verificado = True
                    u.save()
                return redirect("../../../../../../../../../../../../../../../../perfil/")
            return utils.alerta_cliente_perfil(request=request,Alerta="La contraseña actual es incorrecta.")
        return redirect("../../../../../../../../../../../../../../../../../../../")
    



class Eliminar_Cuenta(View):
    def get(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                cliente = models.Cliente.objects.get(userid=request.user)
                request.user.delete()
                cliente.delete()
        return redirect("../../../../../../../../../../../../../")
    

class Nuevo_Mensaje(View):
    def post(self,request):
        cliente=None
        nombre = None
        email=None
        phone = None
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        if asunto == "":
            asunto = None
        if '' in [mensaje]:
            return utils.alerta_cliente_index(request=request,Alerta="El campo de mensaje es obligatorios.")
        if not request.user.is_authenticated:
            nombre = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            if '' in [nombre,email,phone]:
                return utils.alerta_cliente_index(request=request,Alerta="Falta por completar campos obligatorios.")
            nombre = bleach.clean(nombre)
            email = bleach.clean(email)
            phone = bleach.clean(phone)
            if not forms.validate_name(nombre):
                return utils.alerta_cliente_index(request=request,Alerta="El nombre solo admite letras mayúsculas, minúsculas y espacios.")
            if not forms.validar_correo(email,if_existe=False):
                return utils.alerta_cliente_index(request=request,Alerta="Formato de correo electrónico inválido.")
            if not utils.validate_phone_number(phone):
                return utils.alerta_cliente_index(request=request,Alerta="Numero de teléfono inválido.")
        else:
            try:
                cliente = models.Cliente.objects.get(userid=request.user)
            except Exception as e:
                print(e)
                cliente = None
        mensaje = bleach.clean(mensaje)
        nuevo_mensaje=admin_models.Mensaje(clienteid=cliente,nombre=nombre,email=email,phone=phone,asunto=asunto,mensaje=mensaje)
        nuevo_mensaje.save()
        return redirect("../../../../../../../../../../../../../../../../../../../../../")
