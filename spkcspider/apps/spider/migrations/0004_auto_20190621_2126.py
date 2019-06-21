# Generated by Django 2.2.2 on 2019-06-21 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0003_auto_20190621_1954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='linkcontent',
            name='content',
        ),
        migrations.AlterField(
            model_name='assignedcontent',
            name='content_type',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType'),
        ),
    ]
