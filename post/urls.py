from django.conf.urls import patterns, url
from . import views

urlpatterns = [
    # default -> public stream
    url(r'^$', views.public_stream, name='public_stream'),
    url(r'^myStream/$', views.my_stream, name='my_stream'),
    url(r'^post/(?P<post_pk>[0-9]+)/$', views.post_detail, name="post_detail"),

    # redirects here after posting - prevents auto re-submitting form upon page refresh
    url(r'^success/$', views.public_stream, name='public_stream'),  
    url(r'^myStream/success/$', views.public_stream, name='my_stream'),
    
    # url(r'^friendsStream/$', views.friends_stream, name='friends_stream'),
    # url(r'^followsStream/$', views.follows_stream, name='follows_stream'),
]
