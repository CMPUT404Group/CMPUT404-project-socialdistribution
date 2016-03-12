from django.conf.urls import url
from manager import views

urlpatterns = [

    url(r'^manager/$', views.manager, name='manager'),

]

