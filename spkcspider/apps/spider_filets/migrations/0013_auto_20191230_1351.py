# Generated by Django 3.0.1 on 2019-12-30 13:51

from django.db import migrations


def move_to_datacontent(apps, schema_editor):
    AssignedContent = apps.get_model("spider_base", "AssignedContent")
    TextFilet = apps.get_model("spider_filets", "TextFilet")
    FileFilet = apps.get_model("spider_filets", "FileFilet")
    DataContent = apps.get_model("spider_base", "DataContent")

    for a in AssignedContent.objects.filter(
        ctype__code=TextFilet._meta.model_name
    ):
        d = DataContent(associated=a)
        content = TextFilet.objects.get(id=a.object_id)
        d.free_data["push"] = content.push
        d.free_data["editable_from"] = list(content.editable_from.values_list(
            "id", flat=True
        ))
        d.free_data["license_name"] = content.license_name
        d.quota_data["license_url"] = content.license_url
        d.quota_data["sources"] = content.sources
        d.save()
        a.attachedblobs.create(
            unique=True, name="text", blob=content.text.encode("utf8")
        )
    for a in AssignedContent.objects.filter(
        ctype__code=FileFilet._meta.model_name
    ):
        d = DataContent(associated=a)
        content = FileFilet.objects.get(id=a.object_id)
        d.free_data["license_name"] = content.license_name
        d.quota_data["license_url"] = content.license_url
        d.quota_data["sources"] = content.sources
        d.save()
        a.attachedfiles.create(unique=True, name="text", file=content.file)


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0012_auto_20191230_1305'),
        ('spider_filets', '0012_auto_20190419_0800'),
    ]

    operations = [
        migrations.RunPython(move_to_datacontent),
    ]
