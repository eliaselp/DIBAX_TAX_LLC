from django.db import models
from django.contrib.auth.models import User
from cliente.models import Cliente
# Create your models here.

User.add_to_class('tocken', models.TextField(null=True))
User.add_to_class('verificado', models.BooleanField(null=False,default=False))
User.add_to_class('action_verify', models.BooleanField(null=False,default=True))
User.add_to_class('nuevo', models.BooleanField(null=False,default=True))

User.add_to_class('authenticated',models.BooleanField(null=False,default=False))
User.add_to_class('ultimo_login',models.DateTimeField(null=True))
User.add_to_class('antiphishing',models.TextField(null=True,blank=True))


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
    clienteid = models.ForeignKey(Cliente,on_delete=models.SET_NULL,null=True)
    nombre = models.TextField(null=True,blank=True)
    phone = models.TextField(null=True,blank=True)

    fecha = models.DateField(null=False,blank=False)
    hora = models.TimeField(null=True,blank=True)
    
    nueva = models.BooleanField(null=False,blank=False,default=True)
    aprobada = models.BooleanField(null=False,blank=False,default=False)
    finalizada = models.BooleanField(null=False,blank=False,default=False)
    cancelada = models.BooleanField(null=False,blank=False,default=False)

    servicio = models.CharField(max_length=100,null=False,blank=False)
    descripcion = models.TextField(null=True,blank=True)
    detalles = models.TextField(null=True,blank=True)
    importe = models.FloatField(null=True,blank=True)
    factura = models.FloatField(null=True,blank=True)



class Mensaje(models.Model):
    clienteid = models.ForeignKey(Cliente,on_delete=models.SET_NULL,null=True)
    nombre = models.TextField(null=True,blank=True)
    phone = models.TextField(null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    asunto = models.TextField(null=False,blank=False)
    mensaje = models.TextField(null=False,blank=False)
    fecha = models.DateField(auto_now_add=True,null=True)





class Fechas_Bloqueadas(models.Model):
    fecha = models.DateTimeField(null=False,blank=False,unique=True)
