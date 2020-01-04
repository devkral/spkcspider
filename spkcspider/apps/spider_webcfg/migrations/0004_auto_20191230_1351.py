# Generated by Django 3.0.1 on 2019-12-30 13:51

from django.db import migrations


def move_to_datacontent(apps, schema_editor):
    AssignedContent = apps.get_model("spider_base", "AssignedContent")
    WebConfig = apps.get_model("spider_webcfg", "WebConfig")
    DataContent = apps.get_model("spider_base", "DataContent")

    for a in AssignedContent.objects.filter(
        ctype__code=WebConfig._meta.model_name
    ):
        d = DataContent(associated=a)
        content = WebConfig.objects.get(id=a.object_id)
        d.save()
        a.attachedblobs.create(
            unique=True, name="config", blob=content.config
        )


class Migration(migrations.Migration):

    dependencies = [
        ('spider_webcfg', '0003_auto_20190708_1341'),
    ]

    operations = [
        migrations.RunPython(move_to_datacontent),
    ]
