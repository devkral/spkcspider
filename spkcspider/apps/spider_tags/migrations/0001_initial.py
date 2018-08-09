# Generated by Django 2.1 on 2018-08-10 00:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpiderTag',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('tagdata', jsonfield.fields.JSONField(default={})),
                ('verfied_by', jsonfield.fields.JSONField(default=[])),
            ],
            options={
                'abstract': False,
                'default_permissions': ['add'],
            },
        ),
        migrations.CreateModel(
            name='TagLayout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('layout', jsonfield.fields.JSONField(default=[])),
                ('default_verifiers', jsonfield.fields.JSONField(default=[])),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='spidertag',
            name='layout',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tags', to='spider_tags.TagLayout'),
        ),
    ]
