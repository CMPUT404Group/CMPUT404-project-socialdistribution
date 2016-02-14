from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.public_stream, name='public_stream'),	# default -> public stream
]