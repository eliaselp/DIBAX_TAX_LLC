# Generated by Django 5.0.7 on 2024-08-05 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0013_remove_citas_userid_citas_clienteid'),
    ]

    operations = [
        migrations.AddField(
            model_name='citas',
            name='nueva',
            field=models.BooleanField(default=True),
        ),
    ]
