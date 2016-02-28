from django.conf.urls import patterns, url
from . import views

urlpatterns = [
    # default -> public stream
    url(r'^$', views.public_stream, name='public_stream'), 
    url(r'^myStream/$', views.my_stream, name='my_stream'),
    url(r'^post/(?P<post_pk>[0-9]+)/$', views.post_detail, name="post_detail"),
    # url(r'^friendsStream/$', views.friends_stream, name='friends_stream'),
    # url(r'^followsStream/$', views.follows_stream, name='follows_stream'),
]
