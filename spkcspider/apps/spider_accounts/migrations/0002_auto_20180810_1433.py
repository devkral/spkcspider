# Generated by Django 2.1 on 2018-08-10 14:33

from django.db import migrations
import spkcspider.apps.spider_accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('spider_accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='spideruser',
            managers=[
                ('objects', spkcspider.apps.spider_accounts.models.UserManager()),
            ],
        ),
    ]
