# Generated by Django 2.0.5 on 2018-06-06 15:22

from django.conf import settings
from django.db import migrations, models
import spkcspider.apps.spider.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spider_base', '0002_auto_20180606_0012'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercontent',
            options={},
        ),
        migrations.AddField(
            model_name='usercomponent',
            name='nonce',
            field=models.SlugField(default=spkcspider.apps.spider.models.token_nonce, max_length=20),
        ),
        migrations.AddField(
            model_name='usercontent',
            name='nonce',
            field=models.SlugField(default=spkcspider.apps.spider.models.token_nonce, max_length=20),
        ),
        migrations.AlterField(
            model_name='usercontentvariant',
            name='code',
            field=models.CharField(max_length=255),
        ),
        migrations.RemoveField(
            model_name='usercontent',
            name='accessid',
        ),
        migrations.AlterUniqueTogether(
            name='usercontent',
            unique_together={('content_type', 'object_id')},
        ),
        migrations.RemoveField(
            model_name='usercontentvariant',
            name='raw',
        ),
        migrations.AlterUniqueTogether(
            name='usercontentvariant',
            unique_together={('owner', 'name')},
        ),
    ]
