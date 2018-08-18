# Generated by Django 2.1 on 2018-08-10 02:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkContent',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='spider_base.UserContent')),
            ],
            options={
                'abstract': False,
                'default_permissions': [],
            },
        ),
    ]
