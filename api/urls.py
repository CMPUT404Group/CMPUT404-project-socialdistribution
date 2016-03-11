from django.conf.urls import url
from api import views

urlpatterns = [
	url(r'^posts/$', views.PostList.as_view()),
	url(r'^posts/(?P<pk>[^/]+)/$', views.PostDetail.as_view()),
	url(r'^posts/(?P<post_pk>[^/]+)/comments/$', views.CommentList.as_view()),
	url(r'^posts/(?P<post_pk>[^/]+)/comments/(?P<comment_pk>[^/]+)$', views.CommentDetail.as_view()),
	url(r'^users/$', views.UserList.as_view()),
	url(r'^users/(?P<pk>[a-zA-Z0-9]+)/$', views.UserDetail.as_view()),
	url(r'^images/$', views.Images.as_view()),
	url(r'^authors/(?P<author_pk>[^/]+)/$', views.AuthorDetail.as_view()),
	url(r'^authors/$', views.AuthorList.as_view()),

	url(r'^friends/(?P<author_id1>[^/]+)/$',views.FriendingCheck.as_view()),
	url(r'^friends/(?P<author_id1>[^/]+)/(?P<author_id2>[^/]+)/$',views.FriendingCheck.as_view()),

]
