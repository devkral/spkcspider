__all__ = (
    "UpdateProtectionsCallback", "InitUserComponentsCallback",
    "UpdateContentsCallback", "test_success"
)
from django.dispatch import Signal

from django.conf import settings

test_success = Signal(providing_args=["name", "code"])


def UpdateContentsCallback(sender, plan=None, **kwargs):
    # provided apps argument lacks model function support
    # so use this
    from django.apps import apps
    from .contents import initialize_content_models
    initialize_content_models(apps)

    # regenerate info field
    AssignedContent = apps.get_model("spider_base", "AssignedContent")
    for row in AssignedContent.objects.all():
        # works only with django.apps.apps
        row.info = row.content.get_info(row.usercomponent)
        row.save(update_fields=['info'])


def UpdateProtectionsCallback(sender, **kwargs):
    # provided apps argument lacks model function support
    # so use global apps
    from .protections import initialize_protection_models
    initialize_protection_models()


def InitUserComponentsCallback(sender, instance, **kwargs):
    from .models import UserComponent, Protection, AssignedProtection
    uc = UserComponent.objects.get_or_create(name="index", user=instance)[0]
    require_save = False
    login = Protection.objects.filter(code="login").first()
    if login:
        asp = AssignedProtection.objects.get_or_create(
            defaults={"active": True},
            usercomponent=uc, protection=login
        )[0]
        if not asp.active:
            asp.active = True
            require_save = True

    if getattr(settings, "USE_CAPTCHAS", False):
        captcha = Protection.objects.filter(code="captcha").first()
        asp = AssignedProtection.objects.get_or_create(
            defaults={"active": True},
            usercomponent=uc, protection=captcha
        )[0]
        if not asp.active:
            asp.active = True
            require_save = True
    if require_save:
        asp.save()
