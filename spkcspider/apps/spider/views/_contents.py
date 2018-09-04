""" Content Views """

__all__ = (
    "ContentIndex", "ContentAdd", "ContentAccess", "ContentRemove"
)
import json
from collections import OrderedDict
from datetime import timedelta

from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http.response import HttpResponseBase
from django.http import JsonResponse
from django.db import models
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.duration import duration_string

from ._core import UCTestMixin
from ._components import ComponentDelete
from ..constants import UserContentType
from ..models import AssignedContent, ContentVariant, UserComponent
from ..forms import UserContentForm
from ..helpers import get_settings_func


class ContentBase(UCTestMixin):
    model = AssignedContent
    # Views should use one template to render usercontent (whatever it is)
    template_name = 'spider_base/assignedcontent_access.html'
    scope = None
    object = None
    no_nonce_usercomponent = True

    def dispatch(self, request, *args, **kwargs):
        _scope = kwargs.get("access", None)
        if self.scope == "access":
            # special scopes which should be not available as url parameter
            if _scope in ["add", "list"]:
                raise PermissionDenied("Deceptive scopes")
            self.scope = _scope
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs["request"] = self.request
        kwargs["scope"] = self.scope
        kwargs["uc"] = self.usercomponent
        kwargs["enctype"] = "multipart/form-data"
        return super().get_context_data(**kwargs)

    def test_func(self):
        if self.has_special_access(staff=(self.usercomponent.name != "index"),
                                   superuser=True):
            return True
        # block view on special objects for non user and non superusers
        if self.usercomponent.name == "index":
            return False
        return self.test_token()


class ContentAccess(ContentBase, ModelFormMixin, TemplateResponseMixin, View):
    scope = "access"
    form_class = UserContentForm
    model = AssignedContent

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return get_settings_func(
                "RATELIMIT_FUNC",
                "spkcspider.apps.spider.functions.rate_limit_default"
            )(self, request)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = {"form": None}
        if self.scope == "update":
            context["form"] = self.get_form()
        return self.render_to_response(self.get_context_data(**context))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = {"form": None}
        # other than update have no form
        if self.scope == "update":
            context["form"] = self.get_form()
            if context["form"].is_valid():
                self.object = context["form"].save()
                # nonce changed => path has changed
                if self.object.nonce != self.kwargs["nonce"]:
                    return redirect(
                        'spider_base:ucontent-access',
                        id=self.object.id,
                        nonce=self.object.nonce, access="update"
                    )
                context["form"] = self.get_form_class()(
                    **self.get_form_success_kwargs()
                )
        return self.render_to_response(self.get_context_data(**context))

    def get_form_success_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        return {
            'initial': self.get_initial(),
            'instance': self.object,
            'prefix': self.get_prefix()
        }

    def test_func(self):
        if self.scope not in ["update", "raw_update", "export"]:
            return super().test_func()
        # give user and staff the ability to update Content
        # except it is protected, in this case only the user can update
        # reason: admins could be tricked into malicious updates
        # for index the same reason as for add
        uncritically = self.usercomponent.name != "index"
        if self.has_special_access(staff=uncritically, superuser=uncritically):
            return True
        return False

    def render_to_response(self, context):
        if self.scope != "update" or \
           UserContentType.raw_update.value not in self.object.ctype.ctype:
            rendered = self.object.content.render(
                **context
            )
            if UserContentType.raw_update.value in \
               self.object.ctype.ctype:
                return rendered
            # return response if content returned response
            # useful for redirects
            if isinstance(rendered, HttpResponseBase):
                return rendered

            context["content"] = rendered
        if self.scope == "update":
            context["render_in_form"] = True
        return super().render_to_response(context)

    def get_usercomponent(self):
        if self.object:
            return self.object.usercomponent
        return self.get_object().usercomponent

    def get_user(self):
        return self.usercomponent.user

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(
            queryset,
            id=self.kwargs["id"],
            nonce=self.kwargs["nonce"]
        )


class ContentIndex(UCTestMixin, ListView):
    model = AssignedContent
    scope = "list"
    ordering = ("ctype__name", "id")
    no_nonce_usercomponent = False

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return get_settings_func(
                "RATELIMIT_FUNC",
                "spkcspider.apps.spider.functions.rate_limit_default"
            )(self, request)

    def get_usercomponent(self):
        query = {"id": self.kwargs["id"]}
        query["nonce"] = self.kwargs["nonce"]
        return get_object_or_404(UserComponent, **query)

    def get_context_data(self, **kwargs):
        kwargs["uc"] = self.usercomponent
        if self.scope != "export" and "raw" in self.request.GET:
            kwargs["scope"] = "raw"
        else:
            kwargs["scope"] = self.scope

        if kwargs["uc"].user == self.request.user:
            kwargs["content_variants"] = (
                kwargs["uc"].user_info.allowed_content.all()
            )
        return super().get_context_data(**kwargs)

    def test_func(self):
        if self.has_special_access(staff=(self.usercomponent.name != "index"),
                                   superuser=True):
            return True
        # block view on special objects for non user and non superusers
        if self.usercomponent.name == "index":
            return False
        # export is only available for user and superuser
        if self.scope == "export":
            # if self.request.user.is_staff:
            #     return True
            return False

        return self.test_token()

    def get_queryset(self):
        ret = super().get_queryset().filter(usercomponent=self.usercomponent)

        searchq = models.Q()

        counter = 0
        max_counter = 30  # against ddos

        if "search" in self.request.POST or "info" in self.request.POST:
            for info in self.request.POST.getlist("search"):
                if counter > max_counter:
                    break
                counter += 1
                if len(info) > 0:
                    searchq |= models.Q(info__icontains="%s" % info)

            for info in self.request.POST.getlist("info"):
                if counter > max_counter:
                    break
                counter += 1
                searchq |= models.Q(info__contains="\n%s\n" % info)
        else:
            for info in self.request.GET.getlist("search"):
                if counter > max_counter:
                    break
                counter += 1
                if len(info) > 0:
                    searchq |= models.Q(info__icontains="%s" % info)

            for info in self.request.GET.getlist("info"):
                if counter > max_counter:
                    break
                counter += 1
                searchq |= models.Q(info__contains="\n%s\n" % info)

        if "id" in self.request.GET:
            ids = map(lambda x: int(x), self.request.GET.getlist("id"))
            searchq &= models.Q(id__in=ids)
        return ret.filter(searchq)

    def get_paginate_by(self, queryset):
        if self.scope == "export":
            return None
        return getattr(settings, "CONTENTS_PER_PAGE", 25)

    def generate_embedded(self, zip, context):
        # Here export and raw
        deref_level = 2
        if self.scope == "export":
            deref_level = 1
        store_dict = context["store_dict"]
        zip.writestr("data.json", json.dumps(store_dict))
        for n, content in enumerate(context["context"]["object_list"]):
            context["store_dict"] = OrderedDict(
                pk=content.pk,
                ctype=content.ctype.name,
                info=content.info
            )
            content.content.extract_form(
                context, context["store_dict"], zip, level=deref_level,
                prefix="{}/".format(n)
            )
            zip.writestr(
                "{}/data.json".format(n), json.dumps(context["store_dict"])
            )

    def render_to_response(self, context):
        if context["scope"] not in ["export", "raw"]:
            return super().render_to_response(context)

        session_dict = {}
        session_dict["request"] = self.request
        session_dict["context"] = context
        session_dict["uc"] = self.usercomponent

        store_dict = OrderedDict(
            name=self.usercomponent.name,
            scope=context["scope"],
            expires=None  # replaced with expire date of token
        )
        session_dict["store_dict"] = store_dict
        if context["scope"] == "export":
            store_dict["public"] = self.usercomponent.public,
            store_dict["required_passes"] = \
                self.usercomponent.required_passes
            store_dict["token_duration"] = duration_string(
                self.usercomponent.token_duration
            )
        elif hasattr(self.request, "token_expires"):
            store_dict["expires"] = self.request.token_expires.strftime(
                "%a, %d %b %Y %H:%M:%S %z"
            )

        if (
            context["scope"] == "export" or
            self.request.GET.get("raw", "") == "embed"
        ):
            return get_settings_func(
                "GENERATE_EMBEDDED_FUNC",
                "spkcspider.apps.spider.functions.generate_embedded"
            )(self.generate_embedded, session_dict, self.usercomponent)
        hostpart = "{}://{}".format(
            self.request.scheme, self.request.get_host()
        )
        enc_get = context["spider_GET"].urlencode()
        ret = JsonResponse({
            "content": [
                {
                    "info": item.info,
                    "link": "{}{}?{}".format(
                        hostpart,
                        reverse(
                            "spider_base:ucontent-access",
                            kwargs={
                                "id": item.id, "nonce": item.nonce,
                                "access": "view"
                            }
                        ),
                        enc_get
                    )
                }
                for item in context["object_list"]
            ],
            **store_dict
        })
        if store_dict["expires"]:
            ret['X-Token-Expires'] = store_dict["expires"]
        return ret


class ContentAdd(ContentBase, ModelFormMixin,
                 TemplateResponseMixin, View):
    scope = "add"
    model = ContentVariant
    also_authenticated_users = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def test_func(self):
        # test if user and check if user is allowed to create content
        if (
            self.has_special_access(user=True, superuser=False) and
            self.usercomponent.user_info.allowed_content.filter(
                name=self.kwargs["type"]
            ).exists()
        ):
            return True
        return False

    def get_context_data(self, **kwargs):
        kwargs["user_content"] = AssignedContent(
            usercomponent=self.usercomponent,
            ctype=self.object
        )
        kwargs["content_type"] = self.object.installed_class
        form_kwargs = {
            "instance": kwargs["user_content"],
            "initial": {
                "usercomponent": self.usercomponent
            }
        }
        if self.request.method in ('POST', 'PUT'):
            form_kwargs.update({
                'data': self.request.POST,
                # 'files': self.request.FILES,
            })
        kwargs["form"] = UserContentForm(**form_kwargs)
        return super().get_context_data(**kwargs)

    def get_form(self):
        # should never be called
        raise NotImplementedError

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        qquery = models.Q(
            name=self.kwargs["type"],
            strength__lte=self.usercomponent.strength
        )
        return get_object_or_404(queryset, qquery)

    def render_to_response(self, context):
        ucontent = context.pop("user_content")
        ob = context["content_type"].static_create(
            associated=ucontent, **context
        )
        context["render_in_form"] = True
        rendered = ob.render(**ob.kwargs)

        # return response if content returned response
        if isinstance(rendered, HttpResponseBase):
            return rendered
        # show framed output
        context["content"] = rendered
        # redirect if saving worked
        if getattr(ob, "id", None):
            assert(hasattr(ucontent, "id") and ucontent.usercomponent)
            return redirect(
                'spider_base:ucontent-access', id=ucontent.id,
                nonce=ucontent.nonce, access="update"
            )
        return super().render_to_response(context)


class ContentRemove(ComponentDelete):
    model = AssignedContent
    usercomponent = None
    no_nonce_usercomponent = True

    def dispatch(self, request, *args, **kwargs):
        self.usercomponent = self.get_usercomponent()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "spider_base:ucontent-list", kwargs={
                "id": self.usercomponent.id,
                "nonce":  self.usercomponent.nonce
            }
        )

    def get_required_timedelta(self):
        _time = self.object.content.deletion_period
        if _time:
            _time = timedelta(seconds=_time)
        else:
            _time = timedelta(seconds=0)
        return _time

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(
            queryset, usercomponent=self.usercomponent,
            id=self.kwargs["id"], nonce=self.kwargs["nonce"]
        )
