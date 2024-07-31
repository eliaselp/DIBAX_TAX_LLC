# Generated by Django 5.0.7 on 2024-07-31 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Servicios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clase', models.CharField(max_length=100)),
                ('descripcion', models.TimeField(blank=True, null=True)),
                ('precio', models.FloatField(blank=True, null=True)),
                ('urlimagen', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
