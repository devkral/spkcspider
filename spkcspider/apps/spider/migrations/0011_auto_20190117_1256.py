# Generated by Django 2.1.5 on 2019-01-17 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0010_usercomponent_can_auth'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercomponent',
            name='primary_anchor',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(info__contains='\nanchor\n'), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='spider_base.AssignedContent'),
        ),
        migrations.AlterField(
            model_name='authtoken',
            name='persist',
            field=models.BigIntegerField(blank=True, db_index=True, default=-1),
        ),
    ]
