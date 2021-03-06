# Generated by Django 3.0.2 on 2020-01-04 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spider_tags', '0009_auto_20200104_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taglayout',
            name='usertag',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='+', to='spider_base.AssignedContent'),
        ),
        migrations.DeleteModel(
            name='UserTagLayout',
        ),
        migrations.CreateModel(
            name='UserTagLayout',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('spider_base.datacontent',),
        ),
    ]
