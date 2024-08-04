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
    print(contexto)
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
def get_fechas_disponibles(check=None):
    hoy = datetime.now()
    fechas = [(hoy + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(101)]
    fechas_disponibles = []
    for i in fechas:
        fecha_obj = datetime.strptime(i, '%Y-%m-%d')
        dia_semana = fecha_obj.weekday()
        if dia_semana >= 0 and dia_semana < 5:
            if not models.Fechas_Bloqueadas.objects.filter(fecha=i).exists():
                cant_citas = models.Citas.objects.filter(fecha=i)
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