# Generated by Django 2.1.1 on 2018-09-19 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spider_filets', '0004_auto_20180821_0021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filefilet',
            name='add',
        ),
        migrations.RemoveField(
            model_name='filefilet',
            name='modified',
        ),
    ]