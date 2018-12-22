from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from .views import DogView, UserDogView, UserPreferenceView, UserRegisterView

# API endpoints
urlpatterns = format_suffix_patterns([
    url(r'^api/user/login/$', obtain_auth_token, name='login-user'),
    url(r'^api/user/$', UserRegisterView.as_view(), name='register-user'),
    url(r'^favicon\.ico$',
        RedirectView.as_view(
            url='/static/icons/favicon.ico',
            permanent=True
        )),
    url(r'^$', TemplateView.as_view(template_name='index.html')),

    url(r'^api/dog/(?P<pk>\d+)/(?P<liked_status>.+)/next/',
        DogView.as_view(),
        name='dogview'),

    url(r'^api/dog/(?P<pk>-1)/(?P<liked_status>.+)/next/',
        DogView.as_view(),
        name='dogview_minus'),

    url(r'^api/dog/(?P<pk>\d+)/(?P<liked_status>.+)/',
        UserDogView.as_view(),
        name='userdogview'),

    url(r'^api/user/preferences/',
        UserPreferenceView.as_view(),
        name='userpref'),

])
