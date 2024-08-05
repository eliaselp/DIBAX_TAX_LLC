from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout


from App.formularios import LoginForm,Forget_pass_emailForm,TwoFactorForm,Restore_pass_form
from App.correo import enviar_correo
from App.utils import get_tocken,validar_correo,validar_tocken_restore,validar_password,get_metadata
from App.utils import validate_phone_number,get_Servicios,get_fechas_disponibles,validar_fecha
from App.utils import generar_fechas_entre,validate_military_time
from . import models

import uuid
import base64
import bleach
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
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()
                return render(request,'admin/dashboard.html',{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                })
            else:
                email_c = str(request.user.email).encode('utf-8')
                email_c = base64.b64encode(email_c)
                email_c = str(email_c.decode('utf-8'))
                return redirect(f"../../../../../../../../../../../../dibaz_admin/verificacion/{email_c}/")      
        else:
            return redirect("../../../../../../../dibaz_admin/")


#LISTO
class set_Meta(View):
    def post(self,request,tipo):
        if request.user.is_authenticated and request.user.is_staff:
            descripcion = request.POST.get('descripcion')
            if "" in [descripcion, tipo] or tipo not in ['direccion','telefono','email','max_citas']:
                return redirect("../../../../../../../../../../../dibaz_admin/home/")
            if tipo == "telefono" and not validate_phone_number(descripcion)['valid']:
                return render(request,'admin/dashboard.html',{
                    'meta': get_metadata(['email','direccion','telefono','max_citas']),
                    "Alerta":"Numero de telefono inválido"
                })
            if tipo == "email" and not validar_correo(descripcion,if_existe=False):
                return render(request,'admin/dashboard.html',{
                    'meta': get_metadata(['email','direccion','telefono','max_citas']),
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

#LISTO
class Remove_meta(View):
    def get(self,request,tipo):
        if request.user.is_authenticated and request.user.is_staff:
            if tipo in ['direccion','telefono','email']:
                if models.Metadata.objects.filter(tipo=tipo).exists():
                    models.Metadata.objects.get(tipo=tipo).delete()
            return redirect("../../../../../../../../../../../dibaz_admin/home/")
        return redirect("../../../../../../../../../../../../../../../dibaz_admin/")


#LISTO
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
    



#LISTO
class Bloquear_Fecha(View):
    def post(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../../../../")
            desde = request.POST.get("desde")
            hasta = request.POST.get("hasta")
            if desde == "":
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()
                return render(request,'admin/dashboard.html',{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                    "Alerta":"La fecha inicial es requerida."
                })
            if (desde != "" and not validar_fecha(desde)) or (hasta != "" and not validar_fecha(hasta)):
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()
                return render(request,'admin/dashboard.html',{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                    "Alerta":"Formato de Fecha Incorrecto."
                })
            if hasta != "":
                fechas = generar_fechas_entre(inicio=desde,fin=hasta)
                for f in fechas:
                    if not models.Fechas_Bloqueadas.objects.filter(fecha=f).exists():
                        fn = models.Fechas_Bloqueadas(fecha=f)
                        fn.save()
            else:
                if not models.Fechas_Bloqueadas.objects.filter(fecha=desde).exists():
                    fn = models.Fechas_Bloqueadas(fecha=desde)  
                    fn.save()
        return redirect("../../../../../../../../../../../../../../dibaz_admin/")
    

#LISTO
class Habilitar_Fecha(View):
    def post(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../../../../")
            desde = request.POST.get("desde")
            hasta = request.POST.get("hasta")
            if desde == "":
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()
                return render(request,'admin/dashboard.html',{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                    "Alerta":"La fecha inicial es requerida."
                })
            if (desde != "" and not validar_fecha(desde)) or (hasta != "" and not validar_fecha(hasta)):
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()
                return render(request,'admin/dashboard.html',{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                    "Alerta":"Formato de Fecha Incorrecto."
                })
            if hasta != "":
                fechas = generar_fechas_entre(inicio=desde,fin=hasta)
                for f in fechas:
                    if models.Fechas_Bloqueadas.objects.filter(fecha=f).exists():
                        fd = models.Fechas_Bloqueadas.objects.get(fecha=f)
                        fd.delete()
            else:
                if models.Fechas_Bloqueadas.objects.filter(fecha=desde).exists():
                    fd = models.Fechas_Bloqueadas.objects.get(fecha=desde)
                    fd.delete()
        return redirect("../../../../../../../../../../../../../../dibaz_admin/")
    
#LISTO
class Citas_Aprobadas(View):
    def get(self, request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            meta = get_metadata(['email','direccion','telefono','max_citas'])
            servicios,disponibles = get_Servicios()
            citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False).order_by('fecha')
            return render(request,"admin/citas_aprobadas.html",{
                'meta': meta,
                "servicios":servicios,"disponibles":disponibles,
                "fechas_disponibles":get_fechas_disponibles(),
                "citas_aprobadas":citas_aprobadas
            })
        return redirect("../../../../../../../../../../../dibaz_admin/")
    

#LISTO
class Denegar_Cita(View):
    def get(self, request,cita):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            try:
                c = models.Citas.objects.get(id=cita)
                c.nueva = False
                c.aprobada = False
                c.finalizada = True
                c.save()
                if c.clienteid:
                    Asunto = "[DIBAZ TAX LLC] Notificacion de Estado de Solicitud de Cita"
                    Mensaje = f'''
                        Estimado {c.clienteid.userid.username}:

                        Lamentamos informarle que su solicitud de cita para el dia {c.fecha} ha sido denegada.
                        Le pedimos disculpas por cualquier inconveniente que esto pueda causar y le invitamos a ponerse en contacto con nosotros para reprogramar su cita en una fecha y hora más conveniente.

                        Agradecemos su comprensión y estamos a su disposición para cualquier consulta adicional.

                        Atentamente, Soporte DIBAZ TAX LLC
                    '''
                    enviar_correo(c.clienteid.userid.email,Asunto,Mensaje)
                return redirect("../../../../../../../../dibaz_admin/citas_pendientes/")
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../../../dibaz_admin/")    


#LISTO
class Citas_Pendientes(View):
    def get(self, request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            meta = get_metadata(['email','direccion','telefono','max_citas'])
            servicios,disponibles = get_Servicios()
            citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
            return render(request,"admin/citas_pendientes.html",{
                'meta': meta,
                "servicios":servicios,"disponibles":disponibles,
                "fechas_disponibles":get_fechas_disponibles(),
                "citas_pendientes":citas_pendientes
            })
        return redirect("../../../../../../../../../../../dibaz_admin/")

#LISTO
class Agg_Cita(View):
    def post(self, request,servicio):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            if servicio not in ["inmigracion","impuestos","mentoria","consultoria"]:
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()
                return render(request,"admin/dashboard.html",{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                    "Alerta":"Servicio no valido"
                })
            
            nombre = str(request.POST.get("nombre")).strip().title()
            telefono = request.POST.get("telefono")
            descripcion = request.POST.get("descripcion")
            fecha = request.POST.get("fecha")
            detalles = request.POST.get("detalles")
            

            if servicio in ["inmigracion","impuestos"]:
                if "" in [nombre,telefono,descripcion,fecha,detalles]:
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"Todos los campos son obligatorios"
                    })
                nombre = bleach.clean(nombre)
                descripcion = bleach.clean(descripcion)
                detalles = bleach.clean(detalles)
                if not validate_phone_number(telefono)['valid']:
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"Teléfono inválido"
                    })
                descripciones = None
                if servicio == "inmigracion":
                    descripciones = [
                        "Asesoría en Solicitudes de Visas",
                        "Procesamiento de Residencia Permanente (Green Card)",
                        "Ciudadanía y Naturalización",
                        "Renovación y Reemplazo de Documentos",
                        "Defensa en Casos de Deportación",
                        "Otra"
                    ]
                    servicio = "Inmigración"
                elif servicio == "impuestos":
                    descripciones = [
                        "Preparación de Declaraciones de Impuestos",
                        "Planificación Fiscal",
                        "Asesoría en Cumplimiento Tributario",
                        "Resolución de Problemas con el IRS",
                        "Consultoría para Pequeñas Empresas",
                        "Otra"
                    ]
                    servicio = "Impuestos"
                if descripcion not in descripciones:
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"Descripción no válida"
                    })
                
                if not validar_fecha(fecha):
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"Formato de fecha no válido"
                    })
                if not get_fechas_disponibles(check=fecha):
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"La fecha seleccionada no esta disponible"
                    })
                nueva_cita = models.Citas(
                    nombre=nombre,phone=telefono,
                    clienteid=None,fecha=fecha,hora=None,servicio=servicio,
                    descripcion=descripcion,detalles=detalles,importe=None,factura=None,
                    aprobada=False
                )
                nueva_cita.save()
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_pendientes/")
            elif servicio in ["consultoria","mentoria"]:
                if servicio == "consultoria":
                    servicio = "Consultoría"
                elif servicio == "mentoria":
                    servicio = "Mentoría"
                
                if "" in [nombre,telefono,fecha,detalles]:
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"Todos los campos son obligatorios"
                    })
                nombre = bleach.clean(nombre)
                detalles = bleach.clean(detalles)
                if not validate_phone_number(telefono)['valid']:
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"Teléfono inválido"
                    })

                
                if not validar_fecha(fecha):
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"Formato de fecha no válido"
                    })
                if not get_fechas_disponibles(check=fecha):
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    return render(request,"admin/dashboard.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "Alerta":"La fecha seleccionada no esta disponible"
                    })
                nueva_cita = models.Citas(
                    nombre=nombre,phone=telefono,
                    clienteid=None,fecha=fecha,hora=None,servicio=servicio,
                    descripcion=descripcion,detalles=detalles,importe=None,factura=None,
                    aprobada=False
                )
                nueva_cita.save()
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_pendientes/")
        return redirect("../../../../../../../../../../../dibaz_admin/")

#LISTO
class Aprobar_Cita(View):
    def post(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            id = request.POST.get('id')
            cita = None
            try:
                importe = None
                if request.POST.get('importe'):
                    importe = float(request.POST.get('importe'))
                cita = models.Citas.objects.get(id=id,aprobada=False,nueva=True)
                hora = request.POST.get("hora")
                if cita.fecha.strftime('%Y-%m-%d') not in get_fechas_disponibles():
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"La fecha fijada ya no esta disponible."
                    })
                

                

                cita.hora = hora
                if importe:
                    cita.importe = importe
                cita.aprobada = True
                cita.nueva = False
                cita.finalizada = False
                cita.save()
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_aprobadas/")
            except Exception as e:
                print(e)
            return redirect("../../../../../../../../../../../../dibaz_admin/citas_pendientes/")


#LISTO
class Editar_Cita(View):
    def post(self, request,servicio):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            aprobadas = request.POST.get("aprobadas")
            if servicio not in ["Inmigración","Impuestos","Mentoría","Consultoría"]:
                if aprobadas == "true":
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                    return render(request,"admin/citas_aprobadas.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_aprobadas":citas_aprobadas,
                        "Alerta":"Servicio no valido",
                    })
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()
                citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                return render(request,"admin/citas_pendientes.html",{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                    "citas_pendientes":citas_pendientes,
                    "Alerta":"Servicio no valido",
                })
            
            
            id = request.POST.get("id")
            nombre = str(request.POST.get("nombre")).strip().title()
            telefono = request.POST.get("telefono")
            descripcion = request.POST.get("descripcion")
            fecha = request.POST.get("fecha")
            detalles = request.POST.get("detalles")
            hora = request.POST.get("hora")
            importe = request.POST.get("importe")

            if fecha == "":
                fecha = None
            if hora == "":
                hora = None
            if importe == "":
                importe = None
            cita = None
            try:
                cita = models.Citas.objects.get(id=id)
            except Exception as e:
                print(e)
                return redirect("../../../../../../../../../../../../../dibaz_admin/citas_pendientes/")

            if servicio in ["Inmigración","Impuestos"]:
                if "" in [nombre,telefono,descripcion,detalles]:
                    if aprobadas == "true":
                        meta = get_metadata(['email','direccion','telefono','max_citas'])
                        servicios,disponibles = get_Servicios()
                        citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                        return render(request,"admin/citas_aprobadas.html",{
                            'meta': meta,
                            "servicios":servicios,"disponibles":disponibles,
                            "fechas_disponibles":get_fechas_disponibles(),
                            "citas_aprobadas":citas_aprobadas,
                            "Alerta":"Todos los campos son obligatorios"
                        })
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"Todos los campos son obligatorios"
                    })
                    
                nombre = bleach.clean(nombre)
                descripcion = bleach.clean(descripcion)
                detalles = bleach.clean(detalles)
                if not validate_phone_number(telefono)['valid']:
                    if aprobadas == "true":
                        meta = get_metadata(['email','direccion','telefono','max_citas'])
                        servicios,disponibles = get_Servicios()
                        citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                        return render(request,"admin/citas_aprobadas.html",{
                            'meta': meta,
                            "servicios":servicios,"disponibles":disponibles,
                            "fechas_disponibles":get_fechas_disponibles(),
                            "citas_aprobadas":citas_aprobadas,
                            "Alerta":"Teléfono inválido"
                        })
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"Teléfono inválido"
                    })
                descripciones = None
                if servicio == "Inmigración":
                    descripciones = [
                        "Asesoría en Solicitudes de Visas",
                        "Procesamiento de Residencia Permanente (Green Card)",
                        "Ciudadanía y Naturalización",
                        "Renovación y Reemplazo de Documentos",
                        "Defensa en Casos de Deportación",
                        "Otra"
                    ]
                elif servicio == "Impuestos":
                    descripciones = [
                        "Preparación de Declaraciones de Impuestos",
                        "Planificación Fiscal",
                        "Asesoría en Cumplimiento Tributario",
                        "Resolución de Problemas con el IRS",
                        "Consultoría para Pequeñas Empresas",
                        "Otra"
                    ]
                if descripcion not in descripciones:
                    if aprobadas == "true":
                        meta = get_metadata(['email','direccion','telefono','max_citas'])
                        servicios,disponibles = get_Servicios()
                        citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                        return render(request,"admin/citas_aprobadas.html",{
                            'meta': meta,
                            "servicios":servicios,"disponibles":disponibles,
                            "fechas_disponibles":get_fechas_disponibles(),
                            "citas_aprobadas":citas_aprobadas,
                            "Alerta":"Descripción no válida"
                        })
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"Descripción no válida"
                    })
                if (not fecha is None) and (not validar_fecha(fecha)):
                    if aprobadas == "true":
                        meta = get_metadata(['email','direccion','telefono','max_citas'])
                        servicios,disponibles = get_Servicios()
                        citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                        return render(request,"admin/citas_aprobadas.html",{
                            'meta': meta,
                            "servicios":servicios,"disponibles":disponibles,
                            "fechas_disponibles":get_fechas_disponibles(),
                            "citas_aprobadas":citas_aprobadas,
                            "Alerta":"Formato de fecha no válido"
                        })
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"Formato de fecha no válido"
                    })
                if not get_fechas_disponibles(check=fecha):
                    if aprobadas == "true":
                        meta = get_metadata(['email','direccion','telefono','max_citas'])
                        servicios,disponibles = get_Servicios()
                        citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                        return render(request,"admin/citas_aprobadas.html",{
                            'meta': meta,
                            "servicios":servicios,"disponibles":disponibles,
                            "fechas_disponibles":get_fechas_disponibles(),
                            "citas_aprobadas":citas_aprobadas,
                            "Alerta":"La fecha seleccionada no esta disponible"
                        })
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"La fecha seleccionada no esta disponible"
                    })
                if (not hora is None) and (not validate_military_time(hora)):
                    if aprobadas == "true":
                        meta = get_metadata(['email','direccion','telefono','max_citas'])
                        servicios,disponibles = get_Servicios()
                        citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                        return render(request,"admin/citas_aprobadas.html",{
                            'meta': meta,
                            "servicios":servicios,"disponibles":disponibles,
                            "fechas_disponibles":get_fechas_disponibles(),
                            "citas_aprobadas":citas_aprobadas,
                            "Alerta":"Formato de Hora incorrecto"
                        })
                if (not importe is None):
                    try:
                        importe = float(importe)
                    except Exception as e:
                        print(e)
                        if aprobadas == "true":
                            meta = get_metadata(['email','direccion','telefono','max_citas'])
                            servicios,disponibles = get_Servicios()
                            citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                            return render(request,"admin/citas_aprobadas.html",{
                                'meta': meta,
                                "servicios":servicios,"disponibles":disponibles,
                                "fechas_disponibles":get_fechas_disponibles(),
                                "citas_aprobadas":citas_aprobadas,
                                "Alerta":"Formato de importe incorrecto"
                            })
                cita.nombre = nombre
                cita.phone = telefono
                if not fecha is None:
                    cita.fecha = fecha
                if not hora is None:
                    cita.hora = hora
                if not cita.importe is None:
                    cita.importe = importe
                cita.servicio = servicio
                cita.descripcion = descripcion
                cita.detalles = detalles
                
                #cita.factura = None
                cita.save()
                if cita.clienteid:
                    Asunto = "[DIBAZ TAX LLC] Notificacion de Estado de Solicitud de Cita"
                    Mensaje = f'''
                        Estimado {cita.clienteid.userid.username}:

                        Por este medio le informarmamos que su solicitud de cita para el dia {cita.fecha} ha sido modificada.
                        Todos los datos relacionados con dicha cita puede revisarlos en la plataforma.
                        Le pedimos disculpas por cualquier inconveniente que esto pueda causar y le invitamos a ponerse en contacto 
                        con nosotros por cualquier inconveniente.

                        Atentamente, Soporte DIBAZ TAX LLC
                    '''
                    enviar_correo(cita.clienteid.userid.email,Asunto,Mensaje)
                if aprobadas == "true":
                    return redirect("../../../../../../../../../../../dibaz_admin/citas_aprobadas/")
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_pendientes/")
            elif servicio in ["Consultoría","Mentoría"]:    
                if "" in [nombre,telefono,fecha,detalles]:
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"Todos los campos son obligatorios"
                    })
                nombre = bleach.clean(nombre)
                detalles = bleach.clean(detalles)
                if not validate_phone_number(telefono)['valid']:
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"Teléfono inválido"
                    })
                

                if not validar_fecha(fecha):
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"Formato de fecha no válido"
                    })
                    
                if not get_fechas_disponibles(check=fecha):
                    meta = get_metadata(['email','direccion','telefono','max_citas'])
                    servicios,disponibles = get_Servicios()
                    citas_pendientes = list(models.Citas.objects.filter(nueva=True).order_by('id'))
                    return render(request,"admin/citas_pendientes.html",{
                        'meta': meta,
                        "servicios":servicios,"disponibles":disponibles,
                        "fechas_disponibles":get_fechas_disponibles(),
                        "citas_pendientes":citas_pendientes,
                        "Alerta":"La fecha seleccionada no esta disponible"
                    })
                if (not hora is None) and (not validate_military_time(hora)):
                    if aprobadas == "true":
                        meta = get_metadata(['email','direccion','telefono','max_citas'])
                        servicios,disponibles = get_Servicios()
                        citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                        return render(request,"admin/citas_aprobadas.html",{
                            'meta': meta,
                            "servicios":servicios,"disponibles":disponibles,
                            "fechas_disponibles":get_fechas_disponibles(),
                            "citas_aprobadas":citas_aprobadas,
                            "Alerta":"Formato de Hora incorrecto"
                        })
                if (not importe is None):
                    try:
                        importe = float(importe)
                    except Exception as e:
                        print(e)
                        if aprobadas == "true":
                            meta = get_metadata(['email','direccion','telefono','max_citas'])
                            servicios,disponibles = get_Servicios()
                            citas_aprobadas = models.Citas.objects.filter(aprobada=True,finalizada=False,nueva=False)
                            return render(request,"admin/citas_aprobadas.html",{
                                'meta': meta,
                                "servicios":servicios,"disponibles":disponibles,
                                "fechas_disponibles":get_fechas_disponibles(),
                                "citas_aprobadas":citas_aprobadas,
                                "Alerta":"Formato de importe incorrecto"
                            })    
                cita.nombre = nombre
                cita.phone = telefono
                if not fecha is None:
                    cita.fecha = fecha
                if not hora is None:
                    cita.hora = hora
                if not cita.importe is None:
                    cita.importe = importe
                cita.servicio = servicio
                cita.descripcion = descripcion
                cita.detalles = detalles
                
                #cita.factura = None
                cita.save()
                if cita.clienteid:
                    Asunto = "[DIBAZ TAX LLC] Notificacion de Estado de Solicitud de Cita"
                    Mensaje = f'''
                        Estimado {cita.clienteid.userid.username}:

                        Por este medio le informarmamos que su solicitud de cita para el dia {cita.fecha} ha sido modificada.
                        Todos los datos relacionados con dicha cita estan en la plataforma.
                        Le pedimos disculpas por cualquier inconveniente que esto pueda causar y le invitamos a ponerse en contacto 
                        con nosotros por cualquier inconveniente.

                        Atentamente, Soporte DIBAZ TAX LLC
                    '''
                    enviar_correo(cita.clienteid.userid.email,Asunto,Mensaje)
                if aprobadas == "true":
                    return redirect("../../../../../../../../../../../dibaz_admin/citas_aprobadas/")
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_pendientes/")
        return redirect("../../../../../../../../../../../dibaz_admin/")