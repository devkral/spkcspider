# Generated by Django 2.1 on 2018-08-11 12:10

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpiderTag',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('tagdata', jsonfield.fields.JSONField(default={})),
                ('verified_by', jsonfield.fields.JSONField(default=[])),
                ('primary', models.BooleanField(default=False)),
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
                ('name', models.SlugField(max_length=255)),
                ('layout', jsonfield.fields.JSONField(default=[])),
                ('default_verifiers', jsonfield.fields.JSONField(default=[])),
            ],
        ),
        migrations.CreateModel(
            name='UserTagLayout',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
                'default_permissions': ['add'],
            },
        ),
        migrations.AddField(
            model_name='taglayout',
            name='usertag',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='layout', to='spider_tags.UserTagLayout'),
        ),
        migrations.AddField(
            model_name='spidertag',
            name='layout',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tags', to='spider_tags.TagLayout'),
        ),
        migrations.AlterUniqueTogether(
            name='taglayout',
            unique_together={('name', 'usertag')},
        ),
    ]
