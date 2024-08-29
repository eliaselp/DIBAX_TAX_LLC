from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.utils import timezone
from datetime import timedelta

from App.formularios import LoginForm,Forget_pass_emailForm,TwoFactorForm,Restore_pass_form
from App.correo import enviar_correo
from App.utils import get_tocken,validar_correo,validar_tocken_restore,validar_password,get_metadata
from App.utils import validate_phone_number,get_Servicios,get_fechas_disponibles,validar_fecha,validate_username
from App.utils import generar_fechas_entre,validate_military_time,ganancia_total,factura_citas_finalizadas_hoy
from App.utils import sumatoria_facturas_semana_anterior,cantidad_citas_finalizadas_semana_actual
from App.utils import cantidad_citas_finalizadas_mes_actual,cantidad_citas_finalizadas_ano_actual
from App.utils import facturacion_semana_actual,facturacion_mes_actual,facturacion_ano_actual
from App.utils import data_set_citas_semanal,dataset_facturacion_semanal
from App.utils import alerta_dashboard,alerta_citas_aprobadas,alerta_citas_pendientes
from App.utils import actividades_de_hoy
from . import models

import uuid
import base64
import bleach
import datetime
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
                        if u.action_verify == True:
                            u.verificado=False
                            u.save()
                            email_c = str(u.email).encode('utf-8')
                            email_c = base64.b64encode(email_c)
                            email_c = str(email_c.decode('utf-8'))
                            return redirect(f"../../../../../../../../../../../../dibaz_admin/verificacion/{email_c}/")      
                        if request.user.is_staff:
                            return redirect("../../../../../../../../../../../../../dibaz_admin/home/")
                        return redirect("../../../../../../../../../../../../../")
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
            if request.user.is_authenticated and not request.user.antiphishing in [None, ""]:
                Mensaje += f"Código antiphishing: {request.user.antiphishing}"
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
                pass
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
                        pass
                    return redirect(f"../../../../../../../../../../../../../dibaz_admin/restore_pass/{tocken}/")
            else:
                return redirect("../../../../../../../../../dibaz_admin/")
        else:
            return redirect("../../../../../../../../dibaz_admin/home/")








#LISTO
class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.verificado:
                meta = get_metadata(['email','direccion','telefono','max_citas'])
                servicios,disponibles = get_Servicios()

                hace_30_minutos = timezone.now() - timedelta(minutes=30)
                usuarios_authenticated = User.objects.filter(authenticated=True,ultimo_login__gte=hace_30_minutos)

                data_set_citas_semanal__ = list(data_set_citas_semanal())
                max___data_set_citas_semanal = max(data_set_citas_semanal__)
                if max___data_set_citas_semanal == 0:
                    max___data_set_citas_semanal = 10
                dataset_facturacion_semanal__ = dataset_facturacion_semanal()
                max_dataset_facturacion_semanal = max(dataset_facturacion_semanal__)
                if max_dataset_facturacion_semanal == 0:
                    max_dataset_facturacion_semanal = 10

                return render(request,'admin/dashboard.html',{
                    'meta': meta,
                    "servicios":servicios,"disponibles":disponibles,
                    "fechas_disponibles":get_fechas_disponibles(),
                    'citas_de_hoy':actividades_de_hoy(),
                
                    "cantidad_ventas":models.Citas.objects.filter(nueva=False,aprobada=True,finalizada=True).count(),
                    "ganancia_total":ganancia_total(),
                    "cant_citas_pendientes":models.Citas.objects.filter(nueva=True,aprobada=False,finalizada=False).count(),
                    "online":len(usuarios_authenticated),
                    "cant_clients":models.Cliente.objects.all().count(),
                    "cant_client_verify":models.Cliente.objects.filter(Verificado=True).count(),
                    
                    "facturas_hoy":factura_citas_finalizadas_hoy(),
                    "factura_semana_anterior":sumatoria_facturas_semana_anterior(),

                    "cant_citas_semana":cantidad_citas_finalizadas_semana_actual(),
                    "cant_citas_mes":cantidad_citas_finalizadas_mes_actual(),
                    "cant_citas_anio":cantidad_citas_finalizadas_ano_actual(),

                    "facturacion_semana_actual":facturacion_semana_actual(),
                    "facturacion_mes_actual":facturacion_mes_actual(),
                    "facturacion_ano_actual":facturacion_ano_actual(),
                    "data_set_citas_semanal":data_set_citas_semanal__,
                    "max___data_set_citas_semanal":max___data_set_citas_semanal,
                    "dataset_facturacion_semanal":dataset_facturacion_semanal__,
                    "max_dataset_facturacion_semanal":max_dataset_facturacion_semanal,
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
            if tipo == "telefono" and not validate_phone_number(descripcion):
                return alerta_dashboard(request=request,Alerta="Numero de telefono inválido")
            if tipo == "email" and not validar_correo(descripcion,if_existe=False):
                return alerta_dashboard(request=request,Alerta="Correo electronico inválido")
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
            if servicio not in ['inmigracion','impuestos','consultoria']:
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
                return alerta_dashboard(request=request,Alerta="La fecha inicial es requerida.")
            if (desde != "" and not validar_fecha(desde)) or (hasta != "" and not validar_fecha(hasta)):
                return alerta_dashboard(request=request,Alerta="Formato de Fecha Incorrecto.")
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
                return alerta_dashboard(request=request,Alerta="La fecha inicial es requerida.")
            if (desde != "" and not validar_fecha(desde)) or (hasta != "" and not validar_fecha(hasta)):
                return alerta_dashboard(request=request,Alerta="Formato de Fecha Incorrecto.")
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
            return render(request,'admin/citas_aprobadas.html',{
                'meta': meta,
                "servicios":servicios,"disponibles":disponibles,
                "fechas_disponibles":get_fechas_disponibles(),
                'citas_de_hoy':actividades_de_hoy(),
                "citas_aprobadas":citas_aprobadas,
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
                    if cita.clienteid and cita.clienteid.userid.antiphishing != "" and not cita.clienteid.userid.antiphishing is None:
                        Mensaje += f"Código antiphishing: {cita.clienteid.userid.antiphishing}"                    
                    enviar_correo(c.clienteid.userid.email,Asunto,Mensaje)
                return redirect("../../../../../../../../dibaz_admin/citas_pendientes/")
            except Exception as e:
                pass
        return redirect("../../../../../../../../../../../dibaz_admin/")    


#LISTO
class Citas_Pendientes(View):
    def get(self, request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            meta = get_metadata(['email','direccion','telefono','max_citas'])
            servicios,disponibles = get_Servicios()
            citas_pendientes = list(models.Citas.objects.filter(nueva=True,aprobada=False,finalizada=False).order_by('id'))
            return render(request,'admin/citas_pendientes.html',{
                'meta': meta,
                "servicios":servicios,"disponibles":disponibles,
                "fechas_disponibles":get_fechas_disponibles(),
                'citas_de_hoy':actividades_de_hoy(),
                "citas_pendientes":citas_pendientes,
            })
        return redirect("../../../../../../../../../../../dibaz_admin/")

#LISTO
class Agg_Cita(View):
    def post(self, request,servicio):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            if servicio not in ["inmigracion","impuestos","consultoria"]:
                return alerta_dashboard(request=request,Alerta="Servicio no valido")
            
            nombre = str(request.POST.get("nombre")).strip().title()
            telefono = request.POST.get("telefono")
            descripcion = request.POST.get("descripcion")
            fecha = request.POST.get("fecha")
            detalles = request.POST.get("detalles")
            

            if servicio in ["inmigracion","impuestos","consultoria"]:
                if "" in [nombre,telefono,descripcion,fecha,detalles]:
                    return alerta_dashboard(request=request,Alerta="Todos los campos son obligatorios")
                nombre = bleach.clean(nombre)
                descripcion = bleach.clean(descripcion)
                detalles = bleach.clean(detalles)
                if not validate_phone_number(telefono):
                    return alerta_dashboard(request=request,Alerta="Teléfono inválido")
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
                    return alerta_dashboard(request=request,Alerta="Descripción no válida")
                
                if not validar_fecha(fecha):
                    return alerta_dashboard(request=request,Alerta="Formato de fecha no válido")
                if not get_fechas_disponibles(check=fecha):
                    return alerta_dashboard(request=request,Alerta="La fecha seleccionada no esta disponible")
                nueva_cita = models.Citas(
                    nombre=nombre,phone=telefono,
                    clienteid=None,fecha=fecha,hora=None,servicio=servicio,
                    descripcion=descripcion,detalles=detalles,importe=None,factura=None,
                    nueva=True,aprobada=False,finalizada=False
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
                cita = models.Citas.objects.get(id=id,nueva=True,aprobada=False,finalizada=False)
                hora = request.POST.get("hora")
                if cita.fecha.strftime('%Y-%m-%d') not in get_fechas_disponibles():
                    return alerta_citas_pendientes(request=request,Alerta="La fecha fijada ya no esta disponible.")
                        

                cita.hora = hora
                if importe:
                    cita.importe = importe
                cita.nueva = False
                cita.aprobada = True
                cita.finalizada = False
                cita.save()
                if cita.clienteid:
                    Asunto="[DIBAX_TAX_LLC] Confirmación de Aprobación de Cita"

                    Mensaje = f'''
                        Estimado/a {cita.clienteid.userid.username}:
                    
                        Nos complace informarle que su cita para el servicio de {cita.servicio} ha sido aprobada.
                        A continuación, encontrará los detalles de su cita:

                        Fecha: {cita.fecha}
                        Hora: {cita.hora}
                        
                        Si tiene alguna pregunta o necesita realizar algún cambio, no dude en contactarnos.

                        ¡Gracias por elegirnos!

                        Atentamente, DIBAX TAX LLC


                    '''
                    if cita.clienteid and cita.clienteid.userid.antiphishing != "" and not cita.clienteid.userid.antiphishing is None:
                        Mensaje += f"Código antiphishing: {cita.clienteid.userid.antiphishing}"
                    enviar_correo(email=cita.clienteid.userid.email,asunto=Asunto,mensaje=Mensaje)
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_aprobadas/")
            except Exception as e:
                pass
            return redirect("../../../../../../../../../../../../dibaz_admin/citas_pendientes/")


#LISTO
class Editar_Cita(View):
    def post(self, request,servicio):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../")
            aprobadas = request.POST.get("aprobadas")
            if servicio not in ["Trámites migratorios","Impuestos y Emprendimientos","Servicios Consulares Cubanos"]:
                if aprobadas == "true":
                    return alerta_citas_aprobadas(request=request,Alerta="Servicio no valido")
                return alerta_citas_pendientes(request=request,Alerta="Servicio no valido")
                
            
            
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
            if nombre == "":
                nombre = None
            if telefono == "":
                telefono = None
            cita = None
            try:
                cita = models.Citas.objects.get(id=id)
            except Exception as e:
                return redirect("../../../../../../../../../../../../../dibaz_admin/citas_pendientes/")

            if servicio in ["Trámites migratorios","Impuestos y Emprendimientos","Servicios Consulares Cubanos"]:
                if "" in [nombre,telefono,descripcion,detalles]:
                    if aprobadas == "true":
                        return alerta_citas_aprobadas(request=request,Alerta="Todos los campos son obligatorios")
                    return alerta_citas_pendientes(request=request,Alerta="Todos los campos son obligatorios")
                    
                if not nombre is None:
                    nombre = bleach.clean(nombre)
                descripcion = bleach.clean(descripcion)
                detalles = bleach.clean(detalles)
                if (not telefono is None) and (not validate_phone_number(telefono)):
                    if aprobadas == "true":
                        return alerta_citas_aprobadas(request=request,Alerta="Teléfono inválido")
                    return alerta_citas_pendientes(request=request,Alerta="Teléfono inválido")
                    
                descripciones = None
                if servicio == "Trámites migratorios":
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
                elif servicio == "Impuestos y Emprendimientos":
                    descripciones = [
                        "ITIN con Certificado Forense",
                        "Declaración de Impuestos",
                        "Formación de Compañías",
                        "Obtención de EIN",
                        "Traducción de Documentos",
                        "Ministro de Bodas",
                        "Otra"
                    ]
                elif servicio == "Servicios Consulares Cubanos":
                    descripciones = [
                        "Pasaporte",
                        "Visa HE 11",
                        "Autorizacion de Menores",
                        "Visa de Turismo B1/B2",
                        "Poderes y Legalizaciones",
                        "Otra",
                    ]
                if descripcion not in descripciones:
                    if aprobadas == "true":
                        return alerta_citas_aprobadas(request=request,Alerta="Descripción no válida")
                    return alerta_citas_pendientes(request=request,Alerta="Descripción no válida")
                    
                if (not fecha is None) and (not validar_fecha(fecha)):
                    if aprobadas == "true":
                        return alerta_citas_aprobadas(request=request,Alerta="Formato de fecha no válido")
                    return alerta_citas_pendientes(request=request,Alerta="Formato de fecha no válido")
                    
                if (not fecha is None) and (not get_fechas_disponibles(check=fecha)):
                    if aprobadas == "true":
                        return alerta_citas_aprobadas(request=request,Alerta="La fecha seleccionada no esta disponible")
                    return alerta_citas_pendientes(request=request,Alerta="La fecha seleccionada no esta disponible")
                    
                if (not hora is None) and (not validate_military_time(hora)):
                    if aprobadas == "true":
                        return alerta_citas_aprobadas(request=request,Alerta="Formato de Hora incorrecto")
                if (not importe is None):
                    try:
                        importe = float(importe)
                    except Exception as e:
                        if aprobadas == "true":
                            return alerta_citas_aprobadas(request=request,Alerta="Formato de importe incorrecto")
            
                cita.nombre = nombre
                cita.phone = telefono
                if not fecha is None:
                    cita.fecha = fecha
                if not hora is None:
                    cita.hora = hora
                
                cita.importe = importe
                
                cita.descripcion = descripcion
                cita.detalles = detalles
                
                #cita.factura = None
                cita.save()
                if cita.clienteid:
                    Asunto = "[DIBAZ TAX LLC] Notificacion de Replanificación de Cita"
                    Mensaje = f'''
                        Estimado/a {cita.clienteid.userid.username}:

                        Le informamos que su cita ha sido replanificada por el administrador. 
                        
                        Por favor, revise los detalles actualizados en su cuenta o contáctenos si tiene alguna pregunta.

                        Gracias por su comprensión.

                        Saludos cordiales, DIBAZ TAX LLC


                    '''
                    if cita.clienteid and cita.clienteid.userid.antiphishing != "" and not cita.clienteid.userid.antiphishing is None:
                        Mensaje += f"Código antiphishing: {cita.clienteid.userid.antiphishing}"
                    enviar_correo(cita.clienteid.userid.email,Asunto,Mensaje)
                if aprobadas == "true":
                    return redirect("../../../../../../../../../../../dibaz_admin/citas_aprobadas/")
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_pendientes/")
        return redirect("../../../../../../../../../../../dibaz_admin/")


class Finalizar_Cita(View):
    def post(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../../../../../")

            try:
                id = request.POST.get('id')
                cita = models.Citas.objects.get(id=id,nueva=False,aprobada=True,finalizada=False)
                factura = float(request.POST.get("factura"))
                cita.factura = factura
                cita.nueva = False
                cita.aprobada = True
                cita.finalizada = True
                cita.fecha = datetime.datetime.today().date().strftime('%Y-%m-%d')
                cita.save()

                if cita.clienteid:
                    cita.clienteid.Verificado = True
                    cita.clienteid.save()
                return redirect("../../../../../../../../../../../../dibaz_admin/citas_aprobadas/")
            except Exception as e:
                pass
            return alerta_citas_aprobadas(request=request,Alerta="No se ha aprobado la cita.")





class Perfil(View):
    def post(self,request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                username = request.POST.get("username")
                email = request.POST.get("email")
                password0 = request.POST.get("password1")
                password1 = request.POST.get("password2")
                if "" in [username,email]:
                    return alerta_dashboard(request=request,Alerta="Todos los campos son obligatorios")
                username = bleach.clean(username)
                email = bleach.clean(email)
                if username != request.user.username:
                    if not validate_username(username):
                        return alerta_dashboard(request=request,Alerta="El nombre de usuario solo admite letas mayúsculas, minúsculas y números")
                    if User.objects.filter(username=username).exists():
                        return alerta_dashboard(request=request,Alerta="El nombre de usuario esta en uso")
                    request.user.username = username
                    request.user.save()
                if email != request.user.email:
                    if not validar_correo(email,if_existe=False):
                        return alerta_dashboard(request=request,Alerta="Formato de correo electrónico inválido")
                    if User.objects.filter(email=email).exists():
                        return alerta_dashboard(request=request,Alerta="El correo electrónico esta en uso")
                    request.user.email=email
                    request.user.save()
                if password1!="" or password0!="":
                    v = validar_password(password1=password1,password2=password0)
                    if v!="OK":
                        return alerta_dashboard(request=request,Alerta=v)
                    request.user.set_password(password0)
                    request.user.save()
                    u=authenticate(request,username=username, password=password1)
                    if u is not None:
                        auth_login(request, u)                
            else:
                return redirect("../../../../../../../../../../../../../../../../")
        return redirect("../../../../../../../../../../../../../../dibaz_admin/home/")



class Set_2fa(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.action_verify == True:
                request.user.action_verify = False
            else:
                request.user.action_verify = True
            request.user.save()
        return redirect("../../../../../../../../../../../../../dibaz_admin/home/")
    


class Set_antiphishing(View):
    def post(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../../../../../../../../../")
            antiphishing = str(request.POST.get("antiphishing")).strip()
            if "" == antiphishing:
                if request.POST.get("perfil") == "true":
                    return alerta_dashboard(request=request,Alerta="Todos los campos son obligatorios")
                return alerta_dashboard(request=request,Alerta="Todos los campos son obligatorios")
            antiphishing = bleach.clean(str(antiphishing))
            request.user.antiphishing = antiphishing
            request.user.save()
            return redirect("../../../../../../../../../../../../../../../../../../../dibaz_admin/home/")
        return redirect("../../../../../../../../../../../../../../../../../../../dibaz_admin/")



class Delete_antiphishing(View):
    def get(self,request):
        if request.user.is_authenticated:
            request.user.antiphishing = None
            request.user.save()
            return redirect("../../../../../../../../../../../../../../../../../../../dibaz_admin/home/")
        return redirect("../../../../../../../../../../../../../../../../../../../dibaz_admin/")



class Buzon(View):
    def get(self,request):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../../../../../../../../../")
            meta = get_metadata(['email','direccion','telefono','max_citas'])
            servicios,disponibles = get_Servicios()
            return render(request,'admin/buzon.html',{
                'meta': meta,
                "servicios":servicios,"disponibles":disponibles,
                "fechas_disponibles":get_fechas_disponibles(),
                'citas_de_hoy':actividades_de_hoy(),
                "mensajes":models.Mensaje.objects.all(),
            })
        return redirect("../../../../../../../../../../../../../../../../../../../dibaz_admin/")


class Eliminar_Mensaje(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect("../../../../../../../../../../../../../../../../../../../")
            try:
                mensaje = models.Mensaje.objects.get(id=id)
                mensaje.delete()
            except Exception as e:
                pass
            return redirect("../../../../../../../../../../../../../../../../../../../dibaz_admin/buzon/")
        return redirect("../../../../../../../../../../../../../../../../../../../dibaz_admin/")
