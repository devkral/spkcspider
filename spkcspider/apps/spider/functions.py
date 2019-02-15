__all__ = [
    "rate_limit_default", "allow_all_filter",
    "embed_file_default", "has_admin_permission",
    "LimitedTemporaryFileUploadHandler", "validate_url_default",
    "get_quota", "validate_payment_default"
]

import time
import base64
import logging
from decimal import Decimal
from urllib.parse import urlsplit

from django.core.files.uploadhandler import (
    TemporaryFileUploadHandler, StopUpload, StopFutureHandlers
)
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.conf import settings
from rdflib import Literal, XSD

from .signals import failed_guess
from .constants.static import spkcgraph


def rate_limit_default(view, request):
    results = failed_guess.send_robust(sender=view, request=request)
    for (receiver, result) in results:
        if isinstance(result, Exception):
            logging.error(
                "%s failed", receiver, exc_info=result
            )
    time.sleep(1)
    raise Http404()


def allow_all_filter(*args, **kwargs):
    return True


def get_quota(user, quota_type):
    return getattr(user, "quota_{}".format(quota_type), None)


def validate_payment_default(amountstr, cur):
    if len(cur) != 3:
        return None
    return Decimal(amountstr)


class LimitedTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    activated = False

    def handle_raw_input(
        self, input_data, META, content_length, boundary, encoding=None
    ):
        """
        Use the content_length to signal whether or not this handler should be
        used.
        """
        # disable upload if too big
        self.activated = self.check_allowed_size(content_length)

    def new_file(self, *args, **kwargs):
        if not self.activated:
            raise StopFutureHandlers()
        return super().new_file(*args, **kwargs)

    def receive_data_chunk(self, raw_data, start):
        if not self.activated:
            raise StopUpload(True)
        return super().receive_data_chunk(raw_data, start)

    def file_complete(self, file_size):
        """Return a file object if this handler is activated."""
        if not self.activated:
            return
        return super().file_complete(file_size)

    def check_allowed_size(self, content_length):
        if self.request.user.is_staff:
            max_length = getattr(
                settings, "MAX_FILE_SIZE_STAFF", None
            )
        else:
            max_length = getattr(
                settings, "MAX_FILE_SIZE", None
            )
        if not max_length:
            return True

        # admin can upload as much as he wants
        if self.request.user.is_superuser:
            return True

        return content_length <= max_length


def validate_url_default(url, view=None):
    url = urlsplit(url)
    if url.scheme == "https":
        return True
    elif url.scheme == "http":
        # MAKE SURE that you control your dns
        if url.netloc.endswith(".onion"):
            return True
        elif settings.DEBUG:
            return True
    return False


def embed_file_default(name, value, content, context):

    override = (
        (
            context["request"].user.is_superuser or
            context["request"].user.is_staff
        ) and context["request"].GET.get("embed_big", "") == "true"
    )
    if (
        value.size < getattr(settings, "MAX_EMBED_SIZE", 4000000) or
        override
    ):
        return Literal(
            base64.b64encode(value.read()),
            datatype=XSD.base64Binary,
            normalize=False
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
            datatype=spkcgraph["hashableURI"],
        )
    else:
        # only file filet has files yet
        url = content.associated.get_absolute_url("download")
        url = "{}{}?{}".format(
            context["hostpart"],
            url, context["context"]["spider_GET"].urlencode()
        )
        return Literal(
            url,
            datatype=spkcgraph["hashableURI"],
        )


def has_admin_permission(self, request):
    # allow only non travel protected user with superuser and staff permissions
    if not request.user.is_active or not request.user.is_staff:
        return False
    from .models import TravelProtection as TravelProtectionContent
    if TravelProtectionContent.objects.get_active().filter(
        associated_rel__usercomponent__user=request.user
    ).exists():
        return False
    return True


@never_cache
def admin_login(self, request, extra_context=None):
    """
    Display the login form for the given HttpRequest.
    """
    if request.method == 'GET' and self.has_permission(request):
        # Already logged-in, redirect to admin index
        index_path = reverse('admin:index', current_app=self.name)
        return redirect(index_path)
    else:
        loginpath = getattr(
            settings,
            "LOGIN_URL",
            reverse("auth:login")
        )
        return redirect(loginpath)
