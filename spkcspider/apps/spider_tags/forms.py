__all__ = [
    "TagLayoutForm", "SpiderTagForm", "generate_form",
]


from collections import OrderedDict
# from django.utils.translation import gettext_lazy as _
from django import forms

# from django.apps import apps
from django.db.models import Q
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _

from .fields import generate_fields
from .models import TagLayout, SpiderTag


class TagLayoutForm(forms.ModelForm):
    class Meta:
        model = TagLayout
        fields = ["name", "layout", "default_verifiers"]

    def __init__(self, uc=None, **kwargs):
        if "instance" not in kwargs:
            kwargs["instance"] = self._meta.model(usertag=uc)
        super().__init__(**kwargs)


class SpiderTagForm(forms.ModelForm):
    class Meta:
        model = SpiderTag
        fields = ["layout"]

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        index = user.usercomponent_set.get(name="index")
        self.fields["layout"].queryset = self.fields["layout"].queryset.filter(
            Q(usertag__isnull=True) |
            Q(usertag__associated_rel__usercomponent=index)
        ).order_by("name")


def generate_form(name, layout):
    _gen_fields = generate_fields(layout, "tag")
    _gen_fields.insert(0, (
        "primary",
        forms.BooleanField(required=False, initial=False)
    ))

    class _form(forms.BaseForm):
        __name__ = name
        declared_fields = OrderedDict(_gen_fields)
        base_fields = declared_fields
        # used in models
        layout_generating_form = True

        class Meta:
            error_messages = {
                NON_FIELD_ERRORS: {
                    'unique_together': _(
                        'Primary layout for "%s" exists already'
                    ) % name
                }
            }

        def __init__(
            self, *, uc=None, initial=None, usertag=None,
            request=None, **kwargs
        ):
            if not initial:
                initial = {}
            _initial = self.encode_initial(initial)
            _initial["primary"] = getattr(usertag, "primary", False)
            self.usertag = usertag
            super().__init__(
                initial=_initial, **kwargs
            )
            if request.user != uc.user:
                for field in self.fields.values():
                    field.disabled = True
            else:
                for field in self.fields:
                    if hasattr(field, "queryset"):
                        filters = {}
                        attr = getattr(field, "limit_to_usercomponent", None)
                        if attr:
                            filters[attr] = uc
                        attr = getattr(field, "limit_to_user", None)
                        if attr:
                            filters[attr] = uc.user
                        field.queryset = field.queryset.filter(**filters)

        @classmethod
        def encode_initial(cls, initial, prefix="tag", base=None):
            if not base:
                base = {}
            for i in initial.items():
                if isinstance(i[1], dict):
                    new_prefix = "{}:{}".format(prefix, i[0])
                    cls.encode_initial(i[i], prefix=new_prefix, base=base)
                else:
                    base["{}:{}".format(prefix, i[0])] = i[1]
            return base

        @staticmethod
        def encode_data(cleaned_data, embed=False, prefix="tag"):
            ret = OrderedDict()
            for i in cleaned_data.items():
                selected_dict = ret
                splitted = i[0].split(":")
                if splitted[0] != prefix:  # unrelated data
                    continue
                # last key is item key, first is "tag"
                for key in splitted[1:-1]:
                    if key not in selected_dict:
                        selected_dict[key] = OrderedDict()
                    selected_dict = selected_dict[key]
                selected_dict[splitted[-1]] = i[1]
            return ret

        def save(self):
            if self.usertag:
                self.usertag.primary = self.cleaned_data["primary"]
                self.usertag.tagdata = self.encode_data(self.cleaned_data)
                self.usertag.save()

            return self.usertag
    return _form
