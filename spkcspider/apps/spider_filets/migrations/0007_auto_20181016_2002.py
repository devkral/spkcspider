# Generated by Django 2.1.2 on 2018-10-16 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider_filets', '0006_textfilet_preview_words'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textfilet',
            name='preview_words',
            field=models.PositiveIntegerField(default=0, help_text='How many words from start should be used for search, seo, search machine preview? (tags are stripped)'),
        ),
    ]
