# Generated by Django 5.0.7 on 2024-08-04 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicios',
            name='habilitado',
            field=models.BooleanField(default=True),
        ),
    ]
