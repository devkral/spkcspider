from django.conf.urls import url, include
from django.urls import reverse_lazy

from .views import SignupView, UserUpdateView, RecoverView, ResetView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^password_change/$', PasswordChangeView.as_view(success_url=reverse_lazy("auth:password_change_done")), name='password_change'),
    url(r'^password_change/done/$', PasswordChangeDoneView.as_view(), name='password_change_done'),
    # because of the broker and public key recovery only three are required
    #url(r'^recover/$', RecoverView.as_view(), name='password_reset'),
    #url(r'^recover/update/$', ResetView.as_view(), name='password_reset_confirm'),
    #url(r'^recover/done/$', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^signup/$', SignupView.as_view(), name="signup"),
    url(r'^account/$',UserUpdateView.as_view(), name="account"),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('auth:account'), permanent=True)),
    ]
