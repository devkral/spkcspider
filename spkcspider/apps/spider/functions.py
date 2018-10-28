__all__ = [
    "rate_limit_default", "allow_all_filter",
    "embed_file_default", "has_admin_permission"
]

import time
import base64
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings

from rdflib import Literal, XSD


def rate_limit_default(view, request):
    time.sleep(1)
    raise Http404()


def allow_all_filter(*args, **kwargs):
    return True


def validate_file(value):
    max_size = getattr(settings, "MAX_FILE_SIZE", None)
    if max_size and value.size > max_size:
        raise ValidationError(
            _("%(name)s is too big"),
            code='max_size',
            params={'name': value.name},
        )


def embed_file_default(prefix, name, value, context):

    override = (
        (
            context["request"].user.is_superuser or
            context["request"].user.is_staff
        ) and context["request"].GET.get("embed_big", "") == "true"
    )
    if (
        value.size < getattr(settings, "MAX_EMBED_SIZE", 20000000) or
        override
    ):
        return Literal(
            base64.b64encode(value.read()),
            XSD.base64Binary,
            False
        )
    elif (
        context["scope"] == "export" or
        getattr(settings, "DIRECT_FILE_DOWNLOAD", False)
    ):
        # link always direct to files in exports
        url = value.url
        if "://" not in getattr(settings, "MEDIA_URL", ""):
            url = "{}{}".format(context["hostpart"], url)
        return Literal(
            url,
            XSD.anyURI,
        )
    else:
        # only file filet has files yet
        url = context["content"].associated.get_absolute_url("download")
        url = "{}{}?{}".format(
            context["hostpart"],
            url, context["context"]["spider_GET"].urlencode()
        )
        return Literal(
            url,
            XSD.anyURI,
        )


def has_admin_permission(self, request):
    # allow only non faked user with superuser and staff permissions
    if request.session.get("is_fake", False):
        return False
    return request.user.is_active and request.user.is_staff


@never_cache
def admin_login(self, request, extra_context=None):
    """
    Display the login form for the given HttpRequest.
    """
    if request.method == 'GET' and self.has_permission(request):
        # Already logged-in, redirect to admin index
        index_path = reverse('admin:index', current_app=self.name)
        return HttpResponseRedirect(index_path)
    else:
        loginpath = getattr(
            settings,
            "LOGIN_URL",
            reverse("auth:login")
        )
        return HttpResponseRedirect(loginpath)
