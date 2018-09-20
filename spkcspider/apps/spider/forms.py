__all__ = [
    "LinkForm", "UserComponentForm", "UserContentForm",
    "SpiderAuthForm", "TravelProtectionForm"
]

from statistics import mean

from django import forms
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import (
    AssignedProtection, Protection, UserComponent, AssignedContent,
    LinkContent, TravelProtection
)
from .helpers import token_nonce
from .constants import ProtectionType
from .auth import SpiderAuthBackend

_help_text = """Generate new nonce with variable strength<br/>
Nonces protect against bruteforce and attackers<br/>
If you have problems with attackers (because they know the nonce),
you can invalidate it with this option and/or add protections<br/>
<span style="color:red;">
Warning: this removes also access for all services you gave the link<br/>
Warning: if you rely on nonces make sure user component has <em>public</em>
not set
</span>
"""

INITIAL_NONCE_SIZE = str(getattr(settings, "INITIAL_NONCE_SIZE", 12))

NONCE_CHOICES = [
    ("", ""),
    (INITIAL_NONCE_SIZE, _("default ({} Bytes)")),
    ("3", _("low ({} Bytes)")),
    ("12", _("medium ({} Bytes)")),
    ("30", _("high ({} Bytes)")),
]


class UserComponentForm(forms.ModelForm):
    protections = None
    new_nonce = forms.ChoiceField(
        label=_("New Nonce"), help_text=_(_help_text),
        required=False, initial="", choices=NONCE_CHOICES
    )

    class Meta:
        model = UserComponent
        fields = [
            'name', 'public', 'featured', 'required_passes', 'token_duration',
        ]
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _('UserComponent name already exists')
            }
        }

    def __init__(self, request, data=None, files=None, auto_id='id_%s',
                 prefix=None, *args, **kwargs):
        super().__init__(
            *args, data=data, files=files, auto_id=auto_id,
            prefix=prefix, **kwargs
        )
        self.fields["new_nonce"].choices = map(
            lambda c: (c[0], c[1].format(c[0])),
            self.fields["new_nonce"].choices
        )
        if not (
            request.user.is_superuser or
            request.user.has_perm('spider_base.can_feature')
        ) or request.session.get("is_fake", False):
            self.fields['featured'].disabled = True

        if self.instance and self.instance.id:
            assigned = self.instance.protections
            if self.instance.name_protected:
                self.fields["name"].disabled = True
            if self.instance.no_public:
                self.fields["public"].disabled = True
            if self.instance.name in ("fake_index", "index"):
                self.fields["required_passes"].help_text = _(
                    "How many protections must be passed to login?"
                    "Minimum is 1, no matter what selected"
                )
                ptype = ProtectionType.authentication.value
            else:

                ptype = ProtectionType.access_control.value
            self.protections = Protection.get_forms(data=data, files=files,
                                                    prefix=prefix,
                                                    assigned=assigned,
                                                    ptype=ptype)
            self.protections = list(self.protections)
        else:
            self.fields["new_nonce"].initial = INITIAL_NONCE_SIZE
            self.fields["new_nonce"].choices = \
                self.fields["new_nonce"].choices[1:]
            self.protections = []

    def is_valid(self):
        isvalid = super().is_valid()
        for protection in self.protections:
            if not protection.is_valid():
                isvalid = False
        return isvalid

    def clean(self):
        ret = super().clean()
        if not self.instance or not getattr(self.instance, "id", None):
            # TODO: cleanup into protected_names/forbidden_names
            if self.cleaned_data['name'] in ("index", "fake_index"):
                raise forms.ValidationError(
                    _('Forbidden Name'),
                    code="forbidden_name"
                )
        for protection in self.protections:
            protection.full_clean()
        self.cleaned_data["strength"] = 0
        if self.cleaned_data["name"] in ("index", "fake_index"):
            self.cleaned_data["strength"] = 10
            return ret
        if not self.cleaned_data["public"]:
            self.cleaned_data["strength"] += 5

        if self.instance and getattr(self.instance, "id", None):
            fail_strength = 0
            amount_regular = 0
            strengths = []
            for protection in self.protections:
                if not protection.cleaned_data.get("active", False):
                    continue
                if protection.cleaned_data.get("instant_fail", False):
                    fail_strength = max(
                        fail_strength, protection.get_strength()
                    )
                else:
                    strengths.append(protection.get_strength())
                    amount_regular += 1
            strengths.sort()
            if self.cleaned_data["required_passes"] > 0:
                if amount_regular == 0:
                    strengths = 4  # can only access component via own login
                else:
                    strengths = round(mean(strengths[:ret["required_passes"]]))
            else:
                strengths = 0
            self.cleaned_data["strength"] += max(strengths, fail_strength)
        return self.cleaned_data

    def _save_protections(self):
        for protection in self.protections:
            cleaned_data = protection.cleaned_data
            t = AssignedProtection.objects.filter(
                usercomponent=self.instance, protection=protection.protection
            ).first()
            if not cleaned_data["active"] and not t:
                continue
            if not t:
                t = AssignedProtection(
                    usercomponent=self.instance,
                    protection=protection.protection
                )
            t.active = cleaned_data.pop("active")
            t.instant_fail = cleaned_data.pop("instant_fail")
            t.data = cleaned_data
            t.save()

    def _save_m2m(self):
        super()._save_m2m()
        self._save_protections()

    def save(self, commit=True):
        if self.cleaned_data["new_nonce"] != "":
            print(
                "Old nonce for Component id:", self.instance.id,
                "is", self.instance.nonce
            )
            self.instance.nonce = token_nonce(
                int(self.cleaned_data["new_nonce"])
            )

        self.instance.strength = self.cleaned_data["strength"]
        return super().save(commit=commit)


class UserContentForm(forms.ModelForm):
    prefix = "content_control"
    new_nonce = forms.ChoiceField(
        label=_("New Nonce"), help_text=_(_help_text),
        required=False, initial="", choices=NONCE_CHOICES
    )

    class Meta:
        model = AssignedContent
        fields = ['usercomponent']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _(
                    'AssignedContent type/configuration can '
                    'only exist once by usercomponent'
                )
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.usercomponent.user
        query = UserComponent.objects.filter(user=user)
        self.fields["usercomponent"].queryset = query

        self.fields["new_nonce"].choices = map(
            lambda c: (c[0], c[1].format(c[0])),
            self.fields["new_nonce"].choices
        )

        if not self.instance.id:
            self.fields["new_nonce"].initial = INITIAL_NONCE_SIZE
            self.fields["new_nonce"].choices = \
                self.fields["new_nonce"].choices[1:]

    def save(self, commit=True):
        if self.cleaned_data["new_nonce"] != "":
            print(
                "Old nonce for Content id:", self.instance.id,
                "is", self.instance.nonce
            )
            self.instance.nonce = token_nonce(
                int(self.cleaned_data["new_nonce"])
            )
        return super().save(commit=commit)


class SpiderAuthForm(AuthenticationForm):
    password = None
    # can authenticate only with SpiderAuthBackend
    # or descendants, so ignore others
    auth_backend = SpiderAuthBackend()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.reset_protections()

    def reset_protections(self):
        self.request.protections = Protection.authall(
            self.request, scope="auth",
            ptype=ProtectionType.authentication.value,
        )
        # here is not even a usercomponent available
        # if this works, something is wrong
        # protections should match username from POST with the ones of the
        # usercomponent (which is available in clean)
        assert(self.request.protections is not True)

    def clean(self):
        username = self.cleaned_data.get('username')
        protection_codes = None
        if "protection" in self.request.GET:
            protection_codes = self.request.GET.getlist("protection")

        if username is not None:
            self.user_cache = self.auth_backend.authenticate(
                self.request, username=username,
                protection_codes=protection_codes
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class LinkForm(forms.ModelForm):

    class Meta:
        model = LinkContent
        fields = ['content']

    def __init__(self, uc, **kwargs):
        super().__init__(**kwargs)
        q = self.fields["content"].queryset
        travel = TravelProtection.objects.get_active()
        self.fields["content"].queryset = q.filter(
            strength__lte=uc.strength
        ).exclude(travel)


class TravelProtectionForm(forms.ModelForm):
    uc = None
    is_fake = None

    class Meta:
        model = TravelProtection
        fields = [
            "active", "start", "stop", "self_protection", "login_protection",
            "disallow"
        ]

    def __init__(self, uc, is_fake, **kwargs):
        super().__init__(**kwargs)
        self.uc = uc
        self.is_fake = is_fake
        # elif self.travel_protection.is_active:
        #    for f in self.fields:
        #        f.disabled = True
