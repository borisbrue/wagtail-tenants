# Generated by Django 3.2.18 on 2023-10-22 20:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_tenants', '0004_auto_20231022_2039'),
    ]

    operations = [
        migrations.RenameField(
            model_name='smtpauthenticator',
            old_name='use_tsl',
            new_name='use_tls',
        ),
    ]
