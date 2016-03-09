from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'socialDistribution.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='accounts_login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='accounts_logout'),
    url(r'^accounts/signup/$', 'manager.views.register', name='accounts_signup'),
    url(r'^api/', include('api.urls')),
    url(r'', include('post.urls')),
    url(r'^upload/$', 'post.views.file', name='imageupload'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # see https://docs.djangoproject.com/en/dev/howto/static-files/#django.conf.urls.static.static for why this static part should be here for adding media files
