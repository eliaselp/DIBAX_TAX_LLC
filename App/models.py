from django.db import models
from django.contrib.auth.models import User
# Create your models here.

User.add_to_class('tocken', models.TextField(null=True))
User.add_to_class('verificado', models.BooleanField(null=False,default=False))

class Servicios(models.Model):
    clase = models.CharField(max_length=100,null=False,blank=False)
    descripcion = models.TimeField(null=True,blank=True)
    precio = models.FloatField(null=True,blank=True)
    urlimagen = models.TextField(null=True,blank=True)


