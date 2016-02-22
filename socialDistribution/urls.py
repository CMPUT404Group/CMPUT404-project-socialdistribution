from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'socialDistribution.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='accounts_login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='accounts_logout'),
    url(r'^api/', include('api.urls')),
    url(r'', include('post.urls')),
)
