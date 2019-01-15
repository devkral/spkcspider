"""
Protections
namespace: spider_base

"""

__all__ = ["Protection", "AssignedProtection", "AuthToken"]

import logging

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_variables

from jsonfield import JSONField

from ..constants import MAX_NONCE_SIZE, hex_size_of_bigid
from ..helpers import create_b64_token
from ..protections import installed_protections
from ..constants.static import ProtectionType, ProtectionResult, index_names

logger = logging.getLogger(__name__)


class ProtectionManager(models.Manager):
    def invalid(self):
        return self.get_queryset().exclude(code__in=installed_protections)

    def valid(self):
        return self.get_queryset().filter(code__in=installed_protections)


# don't confuse with Protection objects used with add_protection
# this is pure DB
class Protection(models.Model):
    objects = ProtectionManager()
    # autogenerated, no choices required
    code = models.SlugField(max_length=10, primary_key=True, db_index=False)
    # protection abilities/requirements
    ptype = models.CharField(
        max_length=10, default=ProtectionType.authentication.value
    )

    @property
    def installed_class(self):
        return installed_protections[self.code]

    def __str__(self):
        return self.localize_name()

    def __repr__(self):
        return "<Protection: %s>" % self.__str__()

    def localize_name(self):
        if self.code not in installed_protections:
            return self.code
        return self.installed_class.localize_name(self.code)

    def auth_localize_name(self):
        if self.code not in installed_protections:
            return self.code
        return self.installed_class.auth_localize_name(self.code)

    @sensitive_variables("kwargs")
    def auth(self, request, obj=None, **kwargs):
        # never ever allow authentication if not active
        if obj and not obj.active:
            return False
        if self.code not in installed_protections:
            return False
        return self.installed_class.auth(
            obj=obj, request=request, **kwargs.copy()
        )

    @classmethod
    def auth_query(cls, request, query, required_passes=1, **kwargs):
        initial_required_passes = required_passes
        ret = []
        max_result = 0
        for item in query:
            obj = None
            _instant_fail = False
            if hasattr(item, "protection"):  # is AssignedProtection
                item, obj = item.protection, item
                _instant_fail = obj.instant_fail
            # would be surprising if auth fails with required_passes == 0
            # achievable by required_passes = amount of protections
            if initial_required_passes == 0:
                _instant_fail = False
            result = item.auth(
                request=request, obj=obj, query=query,
                required_passes=initial_required_passes, **kwargs
            )
            if _instant_fail:  # instant_fail does not reduce required_passes
                if not isinstance(result,  int):  # False or form
                    # set limit unreachable
                    required_passes = len(query)
                else:
                    if result > max_result:
                        max_result = result
            elif isinstance(result,  int):
                required_passes -= 1
                if result > max_result:
                    max_result = result
            if result is not False:  # False will be not rendered
                ret.append(ProtectionResult(result, item))
        # after side effects like raise Http404
        if (
                request.GET.get("protection", "") == "false" and
                initial_required_passes > 0
           ):
            return False
        # don't require lower limit this way and
        # against timing attacks
        if required_passes <= 0:
            return max_result
        return ret

    @classmethod
    def authall(cls, request, required_passes=1,
                ptype=ProtectionType.authentication.value,
                protection_codes=None, **kwargs):
        """
            Usage: e.g. prerendering for login fields, because
            no assigned object is available there is no config
        """
        query = cls.objects.filter(ptype__contains=ptype)

        # before protection_codes, for not allowing users
        # to manipulate required passes
        if required_passes > 0:
            # required_passes 1 and no protection means: login or token only
            required_passes = max(min(required_passes, len(query)), 1)
        else:
            query = query.filter(
                ptype__contains=ProtectionType.side_effects.value
            )

        if protection_codes:
            query = query.filter(
                code__in=protection_codes
            )
        return cls.auth_query(
            request, query.order_by("code"), required_passes=required_passes,
            ptype=ptype
        )

    def get_form(self, prefix=None, **kwargs):
        if prefix:
            protection_prefix = "{}_protections_{{}}".format(prefix)
        else:
            protection_prefix = "protections_{}"
        return self.installed_class(
            protection=self, prefix=protection_prefix.format(self.code),
            **kwargs
        )

    def render_raw(self, result):
        return {self.code: self.installed_class.render_raw(result)}

    @classmethod
    def get_forms(cls, ptype=None, **kwargs):
        protections = cls.objects.valid()
        if ptype:
            protections = protections.filter(ptype__contains=ptype)
        else:
            ptype = ""
        return map(lambda x: x.get_form(ptype=ptype, **kwargs), protections)


def get_limit_choices_assigned_protection():
    # django cannot serialize static, classmethods
    # possible?????
    index = models.Q(usercomponent__name__in=index_names)
    restriction = models.Q(
        ~index, ptype__contains=ProtectionType.access_control.value
    )
    restriction |= models.Q(
        index, ptype__contains=ProtectionType.authentication.value
    )
    return models.Q(code__in=Protection.objects.valid()) & restriction


class AssignedProtection(models.Model):
    id = models.BigAutoField(primary_key=True)
    # fix linter warning
    objects = models.Manager()
    protection = models.ForeignKey(
        Protection, on_delete=models.CASCADE, related_name="assigned",
        limit_choices_to=get_limit_choices_assigned_protection
    )
    usercomponent = models.ForeignKey(
        "spider_base.UserComponent", related_name="protections",
        on_delete=models.CASCADE, editable=False
    )
    # data for protection
    data = JSONField(default={}, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    active = models.BooleanField(default=True)
    instant_fail = models.BooleanField(
        default=False,
        help_text=_("Auth fails if test fails, stronger than required_passes\n"
                    "Works even if required_passes=0\n"
                    "Does not contribute to required_passes, "
                    "ideal for side effects"
                    )
    )

    class Meta:
        unique_together = [("protection", "usercomponent")]

    def __str__(self):
        return "%s -> %s" % (
            self.usercomponent, self.protection.localize_name()
        )

    def __repr__(self):
        return "<Assigned: %s>" % (
            self.__str__()
        )

    @classmethod
    def authall(cls, request, usercomponent,
                ptype=ProtectionType.access_control.value,
                protection_codes=None, **kwargs):
        query = cls.objects.filter(
            protection__ptype__contains=ptype, active=True,
            usercomponent=usercomponent
        )
        # before protection_codes, for not allowing users
        # to manipulate required passes
        if usercomponent.required_passes > 0:
            required_passes = max(
                min(
                    usercomponent.required_passes,
                    len(query.exclude(instant_fail=True))
                ), 1
            )
        elif usercomponent.name in index_names:
            # enforce a minimum of required_passes, if index
            required_passes = 1
        else:
            required_passes = 0
            # only protections with side effects
            query = query.filter(
                protection__ptype__contains=ProtectionType.side_effects.value
            )

        if protection_codes:
            query = query.filter(
                protection__code__in=protection_codes
            )

        return Protection.auth_query(
            request, query.order_by("protection__code"),
            required_passes=required_passes, ptype=ptype
        )

    @property
    def user(self):
        return self.usercomponent.user


class AuthToken(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    usercomponent = models.ForeignKey(
        "spider_base.UserComponent", on_delete=models.CASCADE,
        related_name="authtokens"
    )
    persist = models.BooleanField(blank=True, default=False, db_index=True)
    # brute force protection
    #  16 = usercomponent.id in hexadecimal
    token = models.SlugField(
        max_length=(MAX_NONCE_SIZE*4//3)+hex_size_of_bigid,
        db_index=True, unique=True
    )
    referrer = models.URLField(
        max_length=400, blank=True, null=True
    )
    created_by_special_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="+", blank=True, null=True
    )
    session_key = models.CharField(max_length=40, null=True)
    extra = JSONField(default={}, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}...".format(self.token[:-_striptoken])

    def create_auth_token(self):
        self.token = "{}_{}".format(
            hex(self.usercomponent.id)[2:],
            create_b64_token(getattr(settings, "TOKEN_SIZE", 30))
        )

    def save(self, *args, **kwargs):
        for i in range(0, 1000):
            if i >= 999:
                raise TokenCreationError(
                    'A possible infinite loop was detected'
                )
            self.create_auth_token()
            try:
                self.validate_unique()
                break
            except ValidationError:
                pass
        super().save(*args, **kwargs)
