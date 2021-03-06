# Generated by Django 2.2 on 2019-04-25 22:07

import django.db.models.deletion
import jsonfield.fields
import spkcspider.apps.spider_keys.models
import spkcspider.apps.spider_keys.forms
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider_keys', '0001_initial'),
    ]
    replaces = [
        ('spider_keys', '0002_0002_20190426_squashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnchorServer',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('new_url', models.URLField(blank=True, help_text='Url to new anchor (in case this one is superseded)', max_length=400, null=True)),
                ('old_urls', jsonfield.fields.JSONField(blank=True, default=list, help_text='Superseded anchor urls')),
            ],
            options={
                'abstract': False,
                'default_permissions': (),
            },
        ),
        migrations.AlterField(
            model_name='publickey',
            name='key',
            field=models.TextField(
                validators=[spkcspider.apps.spider_keys.forms.valid_pkey_properties]),
        ),
        migrations.RemoveField(
            model_name='publickey',
            name='note',
        ),
        migrations.CreateModel(
            name='AnchorKey',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('signature', models.CharField(help_text='Signature of Identifier (hexadecimal-encoded)', max_length=1024)),
                ('key', models.OneToOneField(help_text='"Public Key"-Content for signing identifier. It is recommended to use different keys for signing and encryption. Reason herefor is, that with a change of the signing key the whole anchor gets invalid and the signing key should be really carefully saved away. In contrast the encryption keys can be easily exchanged and should be available for encryption', on_delete=django.db.models.deletion.CASCADE, related_name='anchorkey', to='spider_keys.PublicKey')),
            ],
            options={
                'abstract': False,
                'default_permissions': (),
            },
        ),
    ]
