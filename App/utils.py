import random
def get_tocken():
    lista = list([random.randint(0, 9) for _ in range(6)])
    random.shuffle(lista)
    for x in lista:
        x=str(x)
    return lista




import re
from django.contrib.auth.models import User
def validar_correo(correo,if_existe=True):
    # Definir el patrón de la expresión regular para un correo electrónico válido
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # Usar re.match para verificar si el correo cumple con el patrón
    if re.match(patron, correo):
        if if_existe:
            return User.objects.filter(email=correo).exists()
        return True
    else:
        return False




def validate_military_time(time_string):
    # Expresión regular para validar el formato HH:MM
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    return bool(time_pattern.match(time_string))



def validar_tocken_restore(tocken):
    return User.objects.filter(tocken=tocken).exists()


def validar_password(password1,password2):
    if("" in [password1,password2]):
        return "Todos los campos son obligatorios"
    if(password1!=password2):
        return "Las contraseñas no coinciden"
    if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$', password1):
        return "La contraseña debe tener al menos 8 caracteres, incluyendo números, letras mayúsculas y minúsculas, y caracteres especiales."
    return "OK"



import phonenumbers
from phonenumbers import geocoder, carrier
def validate_phone_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number)
        if phonenumbers.is_valid_number(parsed_number):
            country = geocoder.description_for_number(parsed_number, "en")
            operator = carrier.name_for_number(parsed_number, "en")
            return {
                "valid": True,
                "number": phone_number,
                "country": country,
                "operator": operator
            }
        else:
            return {"valid": False, "message": "Invalid phone number"}
    except phonenumbers.NumberParseException:
        return {"valid": False, "message": "NumberParseException: Invalid format"}
    

from . import models
def get_metadata(tipos):
    a = list(models.Metadata.objects.all())
    contexto = {}
    for i in a:
        if i.tipo in tipos:
            contexto[i.tipo]=i.descripcion
    return contexto

def get_Servicios(estado:str=""):
    servicios={}
    disponibles = 0
    s = list(models.Servicios.objects.all())
    for i in s:
        servicios[i.clase]=i
        if i.habilitado == True:
            disponibles += 1
    disponibles += 4 - (len(s))
    return servicios,disponibles



from datetime import datetime, timedelta
from django.utils import timezone
def get_fechas_disponibles(check=None):
    hoy = timezone.now()
    fechas = [(hoy + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(101)]
    fechas_disponibles = []
    for i in fechas:
        fecha_obj = timezone.make_aware(datetime.strptime(i, '%Y-%m-%d'), timezone.get_current_timezone())
        dia_semana = fecha_obj.weekday()
        if dia_semana >= 0 and dia_semana < 5:
            if not models.Fechas_Bloqueadas.objects.filter(fecha=fecha_obj).exists():
                cant_citas = models.Citas.objects.filter(fecha=fecha_obj.date(), aprobada=True)
                max_citas = 8
                if models.Metadata.objects.filter(tipo="max_citas").exists():
                    max_citas = models.Metadata.objects.get(tipo="max_citas").descripcion
                if len(cant_citas) < int(max_citas):
                    fechas_disponibles.append(i)
    if check is None:
        return fechas_disponibles
    return check in fechas_disponibles

def generar_fechas_entre(inicio, fin):
    fecha_inicio = datetime.strptime(inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fin, '%Y-%m-%d')
    if fecha_inicio > fecha_fin:
        aux = fecha_inicio
        fecha_inicio = fecha_fin
        fecha_fin = aux
    delta = fecha_fin - fecha_inicio
    fechas = [(fecha_inicio + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
    return fechas

def validar_fecha(fecha):
    try:
        datetime.strptime(fecha, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    

def ganancia_total():
    ventas = models.Citas.objects.filter(nueva=False,aprobada=True,finalizada=True)
    return sum(k.factura for k in ventas)

def factura_citas_finalizadas_hoy():
    fecha_actual = datetime.today().date().strftime('%Y-%m-%d')
    citas_finalizadas_hoy = models.Citas.objects.filter(nueva=False,aprobada=True,finalizada=True, fecha=fecha_actual)
    sumatoria_factura = sum(cita.factura for cita in citas_finalizadas_hoy)
    return sumatoria_factura

from django.db.models import Sum
def sumatoria_facturas_semana_anterior():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el lunes de la semana anterior
    lunes_semana_anterior = hoy - timedelta(days=hoy.weekday() + 7)
    # Calcular el domingo de la semana anterior
    domingo_semana_anterior = lunes_semana_anterior + timedelta(days=6)
    # Filtrar las citas finalizadas de la semana anterior y sumar las facturas
    sumatoria = models.Citas.objects.filter(
        nueva=False, aprobada=True,
        finalizada=True,
        fecha__range=[lunes_semana_anterior, domingo_semana_anterior]
    ).aggregate(Sum('factura'))['factura__sum']
    
    return sumatoria if sumatoria else 0.0

def cantidad_citas_finalizadas_semana_actual():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el último lunes antes de hoy
    ultimo_lunes = hoy - timedelta(days=hoy.weekday())
    #hoy = hoy.strftime('%Y-%m-%d')
    #ultimo_lunes = ultimo_lunes.strftime('%Y-%m-%d')
    # Filtrar las citas finalizadas desde el último lunes hasta hoy
    cantidad = models.Citas.objects.filter(
        nueva=False, aprobada=True, finalizada=True,
        fecha__range=[ultimo_lunes, hoy]
    ).count()
    return cantidad

def facturacion_semana_actual():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el último lunes antes de hoy
    ultimo_lunes = hoy - timedelta(days=hoy.weekday())
    # Filtrar las citas finalizadas desde el último lunes hasta hoy
    semana = models.Citas.objects.filter(nueva=False, aprobada=True, finalizada=True, fecha__range=[ultimo_lunes, hoy])
    facturacion = sum(c.factura for c in semana) 
    return facturacion

def cantidad_citas_finalizadas_mes_actual():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el primer día del mes actual
    primer_dia_mes = hoy.replace(day=1)
    # Filtrar las citas finalizadas desde el primer día del mes hasta hoy
    cantidad = models.Citas.objects.filter(
        nueva=False, aprobada=True, finalizada=True,
        fecha__range=[primer_dia_mes, hoy]
    ).count()
    return cantidad


def facturacion_mes_actual():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el primer día del mes actual
    primer_dia_mes = hoy.replace(day=1)
    # Filtrar las citas finalizadas desde el primer día del mes hasta hoy
    mes = models.Citas.objects.filter(nueva=False, aprobada=True, finalizada=True,fecha__range=[primer_dia_mes, hoy])
    facturacion = sum(c.factura for c in mes)
    return facturacion


def cantidad_citas_finalizadas_ano_actual():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el primer día del año actual
    primer_dia_ano = hoy.replace(month=1, day=1)
    # Filtrar las citas finalizadas desde el primer día del año hasta hoy
    cantidad = models.Citas.objects.filter(
        nueva=False, aprobada=True, finalizada=True,
        fecha__range=[primer_dia_ano, hoy]
    ).count()
    return cantidad

def facturacion_ano_actual():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el primer día del año actual
    primer_dia_ano = hoy.replace(month=1, day=1)
    # Filtrar las citas finalizadas desde el primer día del año hasta hoy
    anio = cantidad = models.Citas.objects.filter(nueva=False, aprobada=True, finalizada=True,fecha__range=[primer_dia_ano, hoy])
    facturacion = sum(a.factura for a in anio)
    return facturacion


def data_set_citas_semanal():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el último lunes antes de hoy
    ultimo_lunes = hoy - timedelta(days=hoy.weekday())
    hoy = hoy.strftime('%Y-%m-%d')
    ultimo_lunes = ultimo_lunes.strftime('%Y-%m-%d')
    fechas = generar_fechas_entre(ultimo_lunes,hoy)
    r = []
    for f in fechas:
        r.append(models.Citas.objects.filter(nueva=False, aprobada=True, finalizada=True,fecha=f).count())
    return r

def dataset_facturacion_semanal():
    # Obtener la fecha de hoy
    hoy = datetime.today().date()
    # Calcular el último lunes antes de hoy
    ultimo_lunes = hoy - timedelta(days=hoy.weekday())
    hoy = hoy.strftime('%Y-%m-%d')
    ultimo_lunes = ultimo_lunes.strftime('%Y-%m-%d')
    fechas = generar_fechas_entre(ultimo_lunes,hoy)
    r = []
    for f in fechas:
        r.append(
            sum(k.factura for k in models.Citas.objects.filter(nueva=False, aprobada=True, finalizada=True,fecha=f))
        )
    return r

