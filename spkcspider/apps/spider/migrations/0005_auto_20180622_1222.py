# Generated by Django 2.0.6 on 2018-06-22 12:22

from django.db import migrations, models
import spkcspider.apps.spider.helpers


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0004_auto_20180618_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercomponent',
            name='nonce',
            field=models.SlugField(default=spkcspider.apps.spider.helpers.token_nonce, max_length=120),
        ),
        migrations.AlterField(
            model_name='usercontent',
            name='nonce',
            field=models.SlugField(default=spkcspider.apps.spider.helpers.token_nonce, max_length=120),
        ),
    ]
