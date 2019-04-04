# Generated by Django 2.2 on 2019-04-03 04:17

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('spider_filets', '0009_textfilet_push'),
    ]

    operations = [
        migrations.AddField(
            model_name='filefilet',
            name='license',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='filefilet',
            name='license_name',
            field=models.CharField(default='other', max_length=255),
        ),
        migrations.AddField(
            model_name='filefilet',
            name='sources',
            field=jsonfield.fields.JSONField(default=[], help_text='Sources'),
        ),
        migrations.AddField(
            model_name='textfilet',
            name='license',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='textfilet',
            name='license_name',
            field=models.CharField(default='other', max_length=255),
        ),
        migrations.AddField(
            model_name='textfilet',
            name='sources',
            field=jsonfield.fields.JSONField(default=[], help_text='Sources'),
        ),
    ]
