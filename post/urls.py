from django.conf.urls import patterns, url
from . import views

urlpatterns = [
    # default -> public stream
    url(r'^$', views.public_stream, name='public_stream'),
    url(r'^myStream/$', views.my_stream, name='my_stream'),
    url(r'^post/(?P<post_pk>[^/]+)/$', views.post_detail, name="post_detail"),
    url(r'^post/(?P<post_pk>[^/]+)/edit/$', views.post_edit, name="post_edit"),

    # redirects here after posting - prevents auto re-submitting form upon page refresh
    url(r'^success/$', views.public_stream, name='public_stream_success'),  
    url(r'^myStream/success/$', views.my_stream, name='my_stream_success'),
    url(r'^post/(?P<post_pk>[^/]+)/success/$', views.post_detail, name="post_detail_success"),
    url(r'^author/(?P<username>[a-zA-z0-9-_]+)/success/$', views.user_profile, name="user_profile_success"),

    url(r'^author/(?P<username>[a-zA-z0-9-_]+)/$', views.user_profile, name="user_profile"),
    # url(r'^friendsStream/$', views.friends_stream, name='friends_stream'),
    # url(r'^followsStream/$', views.follows_stream, name='follows_stream'),
]
