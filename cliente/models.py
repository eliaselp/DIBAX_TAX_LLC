from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Cliente(models.Model):
    userid = models.OneToOneField(User,on_delete=models.CASCADE,null=False,blank=False)
    First_Name = models.CharField(max_length=100,null=False,blank=False)
    Last_Name = models.CharField(max_length=100,null=False,blank=False)
    Phone = models.CharField(max_length=12,null=False,blank=False)
    Verificado = models.BooleanField(null=False,default=False)
    