from django import forms

from .models import AssignedProtection, Protection, UserComponent, UserContent
from .protections import ProtectionType


class UserContentForm(forms.ModelForm):

    class Meta:
        fields = ['accessid', 'usercomponent']

    def __init__(self, *args, disabled=True, **kwargs):
        super().__init__(*args, **kwargs)
        if disabled:
            self.fields["accessid"].disabled = True
            self.fields["usercomponent"].disabled = True


class UserComponentForm(forms.ModelForm):
    protections = None

    class Meta:
        model = UserComponent
        fields = ['name']

    def __init__(self, data=None, files=None, auto_id='id_%s',
                 prefix=None, *args, **kwargs):
        super().__init__(
            *args, data=data, files=files, auto_id=auto_id,
            prefix=prefix, **kwargs
        )
        if self.instance and self.instance.id:
            assigned = self.instance.protected_by
            if self.instance.is_protected:
                self.fields["name"].disabled = True
            if self.instance.name == "index":
                ptype = ProtectionType.authentication.value
            else:
                ptype = ProtectionType.access_control.value
            self.protections = Protection.get_forms(data=data, files=files,
                                                    prefix=prefix,
                                                    assigned=assigned,
                                                    ptype=ptype)
            self.protections = list(self.protections)
        else:
            self.protections = []

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance.id:
            if self.instance.is_protected and name != self.instance.name:
                raise forms.ValidationError('Name is protected')

        if name != self.instance.name and UserComponent.objects.filter(
            name=name,
            user=self.instance.user
        ).exists():
            raise forms.ValidationError('Name already exists')
        return name

    def is_valid(self):
        isvalid = super().is_valid()
        for protection in self.protections:
            if not protection.is_valid():
                isvalid = False
        return isvalid

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
            t.data = cleaned_data
            t.save()

    def _save_m2m(self):
        super()._save_m2m()
        self._save_protections()
