# Generated by Django 5.2.1 on 2025-05-27 18:20

import django_ckeditor_5.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='content',
            field=django_ckeditor_5.fields.CKEditor5Field(),
        ),
    ]
