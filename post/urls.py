from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.public_stream, name='public_stream'),	# default -> public stream
	url(r'^myStream/$', views.my_stream, name='my_stream'),
	# url(r'^friendsStream/$', views.friends_stream, name='friends_stream'),
	# url(r'^followsStream/$', views.follows_stream, name='follows_stream'),

]