# Generated by Django 2.1.1 on 2018-10-02 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0005_auto_20180930_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='linkcontent',
            name='is_fake',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
