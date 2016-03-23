from django.conf.urls import url
from api import views

urlpatterns = [
	url(r'^$', views.api_root),
	url(r'^posts/$', views.PostList.as_view(), name='post-list'),
	url(r'^posts/(?P<pk>[^/]+)/$', views.PostDetail.as_view()),
	url(r'^posts/(?P<post_pk>[^/]+)/comments/$', views.CommentList.as_view()),
	url(r'^posts/(?P<post_pk>[^/]+)/comments/(?P<comment_pk>[^/]+)$', views.CommentDetail.as_view()),
	
	url(r'^images/$', views.Images.as_view(), name='images'),

	url(r'^author/$', views.AuthorList.as_view(), name='author-list'),
	url(r'^author/posts$', views.AuthorTimeline.as_view()),
	url(r'^author/(?P<author_pk>[^/]+)/$', views.AuthorDetail.as_view()),
	url(r'^author/(?P<author_pk>[^/]+)/posts$', views.AuthorTimeline.as_view()),

	url(r'^friends/(?P<author_id1>[^/]+)/$',views.FriendingCheck.as_view()),
	url(r'^friends/(?P<author_id1>[^/]+)/(?P<author_id2>[^/]+)/$',views.FriendingCheck.as_view()),

	url(r'^friendrequest/$',views.FriendRequest.as_view(), name='friendrequest'),
	url(r'^friendrequest/(?P<request_pk>[^/]+)$',views.FriendRequest.as_view())

]
