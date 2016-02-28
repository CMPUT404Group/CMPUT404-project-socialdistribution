from django.conf.urls import url
from api import views

urlpatterns = [
	url(r'^posts/$', views.PostList.as_view()),
	url(r'^posts/(?P<pk>[0-9]+)/$', views.PostDetail.as_view()),
	url(r'^posts/(?P<post_pk>[0-9]+)/comments/$', views.CommentList.as_view()),
	url(r'^users/$', views.UserList.as_view()),
	url(r'^users/(?P<pk>[a-zA-Z0-9]+)/$', views.UserDetail.as_view()),

]