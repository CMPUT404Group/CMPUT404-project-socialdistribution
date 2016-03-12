from django.conf.urls import url
from manager import views

urlpatterns = [

    url(r'^manager/$', views.manager, name='manager'),
    url(r'^friendRequest/(?P<username>[a-zA-z0-9-_]+)/$', views.friendRequest, name='friendRequest'),

]

