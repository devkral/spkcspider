# Generated by Django 2.1.7 on 2019-02-25 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0007_usercomponent_allow_domain_mode'),
    ]

    def remove_breaking(apps, schema_editor):
        AuthToken = apps.get_model('spider_base', 'AuthToken')
        AuthToken.objects.filter(referrer__isnull=False).delete()

    operations = [
        migrations.CreateModel(
            name='ReferrerObject',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(db_index=True, editable=False, max_length=600, unique=True)),
            ],
        ),
        migrations.RunPython(remove_breaking),
        migrations.AlterField(
            model_name='authtoken',
            name='referrer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='spider_base.ReferrerObject'),
        ),
    ]
