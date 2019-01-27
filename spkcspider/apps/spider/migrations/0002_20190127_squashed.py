# Generated by Django 2.1.5 on 2019-01-27 14:47

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import spkcspider.apps.spider.models.contents
import spkcspider.apps.spider.models.protections


class Migration(migrations.Migration):

    replaces = [('spider_base', '0002_20181231_squashed'), ('spider_base', '0003_remove_usercomponent_avail_features'), ('spider_base', '0004_auto_20190103_0156'), ('spider_base', '0005_auto_20190109_1505'), ('spider_base', '0006_assignedcontent_priority'), ('spider_base', '0007_linkcontent_push'), ('spider_base', '0008_authtoken_referrer'), ('spider_base', '0009_authtoken_persist'), ('spider_base', '0010_usercomponent_can_auth'), ('spider_base', '0011_auto_20190117_1256'), ('spider_base', '0012_auto_20190118_1017'), ('spider_base', '0013_assignedcontent_persist_token')]

    dependencies = [
        ('spider_base', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='assignedcontent',
            name='strength',
            field=models.PositiveSmallIntegerField(default=0, editable=False, validators=[django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AddField(
            model_name='assignedcontent',
            name='strength_link',
            field=models.PositiveSmallIntegerField(default=0, editable=False, validators=[django.core.validators.MaxValueValidator(11)]),
        ),
        migrations.AddField(
            model_name='contentvariant',
            name='strength',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AddField(
            model_name='usercomponent',
            name='strength',
            field=models.PositiveSmallIntegerField(default=0, editable=False, validators=[django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AlterField(
            model_name='contentvariant',
            name='ctype',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='contentvariant',
            name='name',
            field=models.SlugField(unique=True),
        ),
        migrations.CreateModel(
            name='TravelProtection',
            fields=[
                ('id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=False)),
                ('start', models.DateTimeField(default=spkcspider.apps.spider.models.contents.default_start)),
                ('stop', models.DateTimeField(default=spkcspider.apps.spider.models.contents.default_stop, null=True)),
                ('self_protection', models.BooleanField(default=True, help_text='\n    Disallows user to disable travel protection if active.\n    Can be used in connection with "secret" to allow unlocking via secret\n')),
                ('login_protection', models.CharField(choices=[('a', 'No Login protection')], default='a', help_text='\n    No Login Protection: normal, default\n    Fake Login: fake login and index (experimental)\n    Wipe: Wipe protected content,\n    except they are protected by a deletion period\n    Wipe User: destroy user on login\n\n\n    <div>\n        Danger: every option other than: "No Login Protection" can screw you.\n        "Fake Login" can trap you in a parallel reality\n    </div>\n', max_length=10)),
                ('secret', models.SlugField(default='', max_length=120)),
            ],
            options={
                'abstract': False,
                'default_permissions': [],
            },
        ),
        migrations.AlterField(
            model_name='assignedprotection',
            name='protection',
            field=models.ForeignKey(limit_choices_to=spkcspider.apps.spider.models.protections.get_limit_choices_assigned_protection, on_delete=django.db.models.deletion.CASCADE, related_name='assigned', to='spider_base.Protection'),
        ),
        migrations.AlterField(
            model_name='usercomponent',
            name='deletion_requested',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='usercomponent',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='travelprotection',
            name='disallow',
            field=models.ManyToManyField(blank=True, related_name='travel_protected', to='spider_base.UserComponent'),
        ),
        migrations.AlterModelOptions(
            name='usercomponent',
            options={'permissions': [('can_feature', 'Can feature User Components')]},
        ),
        migrations.AddField(
            model_name='usercomponent',
            name='featured',
            field=models.BooleanField(default=False, help_text='Appears as featured on "home" page'),
        ),
        migrations.AlterField(
            model_name='usercomponent',
            name='name',
            field=models.SlugField(allow_unicode=True, help_text='\nName of the component.<br/>\nNote: there are special named components\nwith different protection types and scopes.<br/>\nMost prominent: "index" for authentication\n'),
        ),
        migrations.AddField(
            model_name='usercomponent',
            name='description',
            field=models.TextField(blank=True, default='', help_text='Description of user component.'),
        ),
        migrations.AddField(
            model_name='assignedcontent',
            name='fake_id',
            field=models.BigIntegerField(editable=False, null=True),
        ),
        migrations.RemoveField(
            model_name='travelprotection',
            name='secret',
        ),
        migrations.RemoveField(
            model_name='travelprotection',
            name='self_protection',
        ),
        migrations.AddField(
            model_name='travelprotection',
            name='hashed_secret',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='assignedcontent',
            name='references',
            field=models.ManyToManyField(editable=False, related_name='referenced_by', to='spider_base.AssignedContent'),
        ),
        migrations.AddField(
            model_name='authtoken',
            name='created_by_special_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='authtoken',
            name='extra',
            field=jsonfield.fields.JSONField(blank=True, default={}),
        ),
        migrations.AlterField(
            model_name='travelprotection',
            name='login_protection',
            field=models.CharField(choices=[('a', 'No Login protection'), ('b', 'Fake login'), ('c', 'Wipe'), ('d', 'Wipe User')], default='a', help_text='\n    No Login Protection: normal, default\n    Fake Login: fake login and index (experimental)\n    Wipe: Wipe protected content,\n    except they are protected by a deletion period\n    Wipe User: destroy user on login\n\n\n    <div>\n        Danger: every option other than: "No Login Protection" can screw you.\n        "Fake Login" can trap you in a parallel reality\n    </div>\n', max_length=10),
        ),
        migrations.AddField(
            model_name='travelprotection',
            name='is_fake',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='travelprotection',
            name='login_protection',
            field=models.CharField(choices=[('a', 'No Login protection'), ('b', 'Fake login'), ('c', 'Wipe'), ('d', 'Wipe User')], default='a', help_text='No Login Protection: normal, default<br/>Fake Login: fake login and index<br/>Wipe: Wipe protected content, except they are protected by a deletion period<br/>Wipe User: destroy user on login', max_length=10),
        ),
        migrations.AlterField(
            model_name='usercomponent',
            name='name',
            field=models.SlugField(allow_unicode=True, help_text='Name of the component.<br/>Note: there are special named components with different protection types and scopes.<br/>Most prominent: "index" for authentication'),
        ),
        migrations.AddField(
            model_name='usercomponent',
            name='features',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(ctype__contains='a'), related_name='supports', to='spider_base.ContentVariant'),
        ),
        migrations.AlterField(
            model_name='assignedcontent',
            name='ctype',
            field=models.ForeignKey(editable=False, limit_choices_to=models.Q(_negated=True, ctype__contains='a'), null=True, on_delete=django.db.models.deletion.SET_NULL, to='spider_base.ContentVariant'),
        ),
        migrations.AlterField(
            model_name='authtoken',
            name='token',
            field=models.SlugField(max_length=136, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='authtoken',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='assignedcontent',
            name='ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='spider_base.ContentVariant'),
        ),
        migrations.RenameField(
            model_name='userinfo',
            old_name='used_space',
            new_name='used_space_local',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='used_space_remote',
            field=models.BigIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='assignedcontent',
            name='priority',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='linkcontent',
            name='push',
            field=models.BooleanField(blank=True, default=False, help_text='Push Link to top.'),
        ),
        migrations.AddField(
            model_name='authtoken',
            name='referrer',
            field=models.URLField(blank=True, max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='authtoken',
            name='persist',
            field=models.BigIntegerField(blank=True, db_index=True, default=-1),
        ),
        migrations.AddField(
            model_name='usercomponent',
            name='can_auth',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='usercomponent',
            name='primary_anchor',
            field=models.ForeignKey(blank=True, help_text='Select main identyifing anchor. Also used for attaching persisting tokens (elsewise they are attached to component)', limit_choices_to={'info__contains': '\nanchor\n'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_anchor_for', to='spider_base.AssignedContent'),
        ),
        migrations.AlterField(
            model_name='linkcontent',
            name='content',
            field=models.ForeignKey(limit_choices_to={'strength_link__lte': 10}, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='spider_base.AssignedContent'),
        ),
        migrations.AlterField(
            model_name='usercomponent',
            name='public',
            field=models.BooleanField(default=False, help_text='Is public? Is listed and searchable?<br/>Note: This field is maybe not deactivatable because of assigned content'),
        ),
        migrations.AddField(
            model_name='assignedcontent',
            name='persist_token',
            field=models.ForeignKey(blank=True, limit_choices_to={'persist__gte': 0}, null=True, on_delete=django.db.models.deletion.CASCADE, to='spider_base.AuthToken'),
        ),
    ]
