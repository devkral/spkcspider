# Generated by Django 2.1.4 on 2018-12-31 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider_webcfg', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webconfig',
            name='creation_url',
            field=models.URLField(
                default='https://spkcspider.net/', editable=False
            ),
            preserve_default=False,
        ),
    ]
