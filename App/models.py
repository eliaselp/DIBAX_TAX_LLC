from django.db import models
from django.contrib.auth.models import User
# Create your models here.

User.add_to_class('tocken', models.TextField(null=True))
User.add_to_class('verificado', models.BooleanField(null=False,default=False))
User.add_to_class('action_verify', models.BooleanField(null=False,default=True))
User.add_to_class('nuevo', models.BooleanField(null=False,default=True))

class Servicios(models.Model):
    clase = models.CharField(max_length=100,null=False,blank=False)
    habilitado = models.BooleanField(null=False,default=True)
    descripcion = models.TimeField(null=True,blank=True)
    precio = models.FloatField(null=True,blank=True)
    urlimagen = models.TextField(null=True,blank=True)


class Metadata(models.Model):
    tipo = models.TextField(null=False,blank=False,unique=True)
    descripcion = models.TextField(null=False, blank=False)


class Citas(models.Model):
    fecha = models.DateField(null=False,blank=False)
    servicio = models.CharField(max_length=100,null=False,blank=False)
    descripcion = models.TextField(null=False,blank=False)
    importe = models.FloatField(null=True,blank=True)
    factura = models.FloatField(null=True,blank=True)


class Fechas_Bloqueadas(models.Model):
    fecha = models.DateTimeField(null=False,blank=False,unique=True)
