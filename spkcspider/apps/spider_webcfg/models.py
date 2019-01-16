__all__ = ["WebConfig"]

from django.db import models
from django.urls import reverse

from spkcspider.apps.spider.constants.static import VariantType
from spkcspider.apps.spider.contents import BaseContent, add_content


@add_content
class WebConfig(BaseContent):
    appearances = [
        {
            "name": "WebConfig",
            "ctype": (
                VariantType.unique + VariantType.feature + VariantType.persist
            ),
            "strength": 0
        }
    ]

    token = models.ForeignKey(
        "spider_base.AuthToken", limit_choices_to={"persist": True},
        on_delete=models.CASCADE
    )
    creation_url = models.URLField(editable=False)
    config = models.TextField(default="", blank=True)

    @classmethod
    def action_url(cls):
        return reverse("spider_webcfg:webconfig-view")

    def get_size(self):
        return len(self.config)

    def get_priority(self):
        # low priority
        return -10

    def get_form_kwargs(self, **kwargs):
        ret = super().get_form_kwargs(**kwargs)
        ret["scope"] = kwargs["scope"]
        ret["user"] = kwargs["request"].user
        return ret

    def get_form(self, scope):
        from .forms import WebConfigForm as f
        return f

    def get_info(self):
        ret = super().get_info(unique=True)
        return "{}url={}\n".format(
            ret, self.token.referrer.replace("\n", "%0A")
        )