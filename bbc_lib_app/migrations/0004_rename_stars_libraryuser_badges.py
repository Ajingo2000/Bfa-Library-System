# Generated by Django 4.1.2 on 2023-08-14 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bbc_lib_app', '0003_libraryuser_stars'),
    ]

    operations = [
        migrations.RenameField(
            model_name='libraryuser',
            old_name='stars',
            new_name='badges',
        ),
    ]