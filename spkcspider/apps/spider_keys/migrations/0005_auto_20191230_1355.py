# Generated by Django 3.0.1 on 2019-12-30 13:55

from django.db import migrations


def move_to_datacontent(apps, schema_editor):
    AssignedContent = apps.get_model("spider_base", "AssignedContent")
    AnchorKey = apps.get_model("spider_keys", "AnchorKey")
    AnchorServer = apps.get_model("spider_keys", "AnchorServer")
    PublicKey = apps.get_model("spider_keys", "PublicKey")
    DataContent = apps.get_model("spider_base", "DataContent")

    for a in AssignedContent.objects.filter(
        ctype__code=PublicKey._meta.model_name
    ):
        d = DataContent(associated=a)
        content = PublicKey.objects.get(id=a.object_id)
        d.save()
        a.attachedblob_set.create(
            unique=True, name="key", blob=content.key.encode("utf8")
        )

    for a in AssignedContent.objects.filter(
        ctype__code=AnchorKey._meta.model_name
    ):
        d = DataContent(associated=a)
        content = AnchorKey.objects.get(id=a.object_id)
        d.quota_data["signature"] = content.signature
        d.save()

    for a in AssignedContent.objects.filter(
        ctype__code=AnchorServer._meta.model_name
    ):
        d = DataContent(associated=a)
        content = AnchorServer.objects.get(id=a.object_id)
        d.quota_data["new_url"] = content.new_url
        d.quota_data["old_urls"] = content.old_urls
        d.save()


class Migration(migrations.Migration):

    dependencies = [
        ('spider_base', '0012_auto_20191230_1305'),
        ('spider_keys', '0004_remove_anchorkey_key'),
    ]

    operations = [
        migrations.RunPython(move_to_datacontent),
    ]
