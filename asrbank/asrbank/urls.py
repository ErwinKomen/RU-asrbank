"""
Definition of urls for asrbank.
"""

from datetime import datetime
from django.conf.urls import url
from django.core import urlresolvers
import django.contrib.auth.views

import asrbank.transcription.forms
from asrbank.transcription.views import *

# Uncomment the next lines to enable the admin:
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.contrib import admin
import nested_admin
from asrbank.settings import APP_PREFIX, STATIC_ROOT, STATIC_URL

admin.autodiscover()

# set admin site names
admin.site.site_header = 'ASR Bank Admin'
admin.site.site_title = 'ASR Bank Site Admin'

# define a site prefix: SET this for the production environment
pfx = APP_PREFIX


urlpatterns = [
    # Examples:
    url(r'^$', asrbank.transcription.views.home, name='home'),
    url(r'^contact$', asrbank.transcription.views.contact, name='contact'),
    url(r'^about', asrbank.transcription.views.about, name='about'),
    url(r'^definitions$', RedirectView.as_view(url='/'+pfx+'admin/'), name='definitions'),
    url(r'^registry', RedirectView.as_view(url='/'+pfx+'admin/transcription/descriptor/'), name='registry'),
    url(r'^overview/$', DescriptorListView.as_view(), name='overview'),
    url(r'^output/(?P<pk>\d+)', DescriptorDetailView.as_view(), name='output'),
    url(r'^signup/$', asrbank.transcription.views.signup, name='signup'),

    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'transcription/login.html',
            'authentication_form': asrbank.transcription.forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': reverse_lazy('home'),
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^_nested_admin/', include('nested_admin.urls')),
]
