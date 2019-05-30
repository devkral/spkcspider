# Generated by Django 2.2.1 on 2019-05-30 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('spider_verifier', '0002_auto_20181031_2121'), ('spider_verifier', '0003_1_linked_hashes_stub'), ('spider_verifier', '0004_auto_20190225_2153'), ('spider_verifier', '0005_auto_20190302_1741'), ('spider_verifier', '0006_verifysourceobject_update_secret'), ('spider_verifier', '0007_auto_20190530_1636')]

    dependencies = [
        ('spider_verifier', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataverificationtag',
            options={'permissions': [('can_verify', 'Can verify Data Tag?')]},
        ),
        migrations.AlterField(
            model_name='dataverificationtag',
            name='note',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='dataverificationtag',
            name='verification_state',
            field=models.CharField(choices=[('retrieve', 'retrieval pending'), ('pending', 'pending'), ('verified', 'verified'), ('invalid', 'invalid'), ('rejected', 'rejected')], default='retrieve', max_length=10),
        ),
        migrations.AddField(
            model_name='dataverificationtag',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='spider_verifier.VerifySourceObject'),
        ),
        migrations.AlterField(
            model_name='dataverificationtag',
            name='verification_state',
            field=models.CharField(choices=[('pending', 'pending'), ('verified', 'verified'), ('invalid', 'invalid'), ('rejected', 'rejected')], default='pending', max_length=10),
        ),
        migrations.AddField(
            model_name='verifysourceobject',
            name='token',
            field=models.CharField(blank=True, max_length=126, null=True, unique=True),
        ),
    ]
