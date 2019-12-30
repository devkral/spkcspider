# Generated by Django 3.0.1 on 2019-12-30 13:05

from django.db import migrations


def move_to_datacontent(apps, schema_editor):
    AssignedContent = apps.get_model("spider_base", "AssignedContent")
    LinkContent = apps.get_model("spider_base", "LinkContent")
    TravelProtection = apps.get_model("spider_base", "TravelProtection")
    DataContent = apps.get_model("spider_base", "DataContent")

    for a in AssignedContent.objects.filter(
        ctype__name="Link"
    ):
        d = DataContent(associated=a)
        content = LinkContent.objects.get(id=a.object_id)
        d.free_data["push"] = content.push
        d.save()

    for a in AssignedContent.objects.filter(
        ctype__code=TravelProtection._meta.model_name
    ):
        content = TravelProtection.objects.get(id=a.object_id)
        content.associated = a
        d.save()


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0010_auto_20191230_1300'),
    ]

    operations = [
        migrations.RunPython(move_to_datacontent),
    ]
