# Generated by Django 2.1.5 on 2019-01-15 02:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('spider_base', '0002_20190518_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebConfig',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('creation_url', models.URLField(editable=False)),
                ('config', models.TextField(blank=True, default='')),
                ('token', models.ForeignKey(limit_choices_to={'persist': True}, on_delete=django.db.models.deletion.CASCADE, to='spider_base.AuthToken')),
            ],
            options={
                'abstract': False,
                'default_permissions': (),
            },
        ),
    ]
