# Generated by Django 4.1.2 on 2023-08-01 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbc_lib_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryuser',
            name='qr_code_image',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]