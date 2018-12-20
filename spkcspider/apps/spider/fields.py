__all__ = ["OpenChoiceField", "SanitizedHtmlField"]

from django.forms import fields

from html5lib.filters.sanitizer import allowed_css_properties
from bleach import sanitizer

from .widgets import OpenChoiceWidget, TrumbowygWidget


class OpenChoiceField(fields.MultipleChoiceField):
    widget = OpenChoiceWidget
    validate_choice = None

    def __init__(
        self, *, choices=(), initial=None, validate_choice=None, **kwargs
    ):
        super().__init__(choices=choices, **kwargs)
        self.validate_choice = validate_choice

    def valid_value(self, value):
        if not self.validate_choice:
            return True
        return self.validate_choice(value)


class SanitizedHtmlField(fields.Field):
    widget = TrumbowygWidget

    # for an unsanitized Field just use TrumbowygWidget with a CharField

    allowed_css_properties = allowed_css_properties

    default_allowed_tags = sanitizer.ALLOWED_TAGS + [
        'img', 'p', 'br', 'sub', 'sup', 'h1', 'h2', 'h3', 'h4', 'pre',
        'del', 'audio', 'source', 'video'
    ]
    default_allowed_protocols = sanitizer.ALLOWED_PROTOCOLS + [
        'data', 'mailto'
    ]

    cleaner = sanitizer.Cleaner(
        tags=default_allowed_tags,
        attributes=lambda tag, name, value: True,
        styles=allowed_css_properties,
        protocols=default_allowed_protocols
    )

    def check_attrs_func(tag, name, value):
        # currently no restrictions
        return True

    def __init__(self, *, cleaner=None, **kwargs):
        if cleaner:
            self.cleaner = cleaner
        super().__init__(**kwargs)

    def to_python(self, value):
        """Return a string."""
        return self.cleaner.clean(value)
