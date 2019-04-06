from django import template
from django.urls import reverse
from django.utils import timezone

register = template.Library()


@register.filter()
def is_not_or_space(value):
    if not value:
        return True
    return isinstance(value, str) and value.isspace()


@register.simple_tag(takes_context=True)
def list_own_content(context):
    ucname = "index"
    if context["request"].session.get("is_fake", False):
        ucname = "fake_index"
    if context["request"].user.is_authenticated:
        return context["request"].user.usercomponent_set.get(
            name=ucname
        ).get_absolute_url()
    return ""


@register.simple_tag(takes_context=True)
def update_component(context, name):
    ucname = name
    if ucname == "index" and context["request"].session.get("is_fake", False):
        ucname = "fake_index"
    if context["request"].user.is_authenticated:
        uc = context["request"].user.usercomponent_set.only("token").get(
            name=ucname
        )
        return reverse("spider_base:ucomponent-update", kwargs={
            "token": uc.token
        })
    return ""


@register.simple_tag(takes_context=True)
def reverse_get(context, name, **kwargs):
    """ Works only if hostpart and spider_GET is available """
    return "{}{}?{}".format(
        context["hostpart"],
        reverse(name, kwargs=kwargs),
        context["spider_GET"].urlencode()
    )


@register.simple_tag()
def concat_string(*args):
    return "".join(args)


@register.simple_tag()
def expires_delta(expires):
    return expires-timezone.now()


@register.simple_tag()
def token_expires(usercomponent, token):
    return token.created + usercomponent.token_duration
