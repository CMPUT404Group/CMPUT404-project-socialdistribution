from django.shortcuts import render
from django.utils import timezone
from api.models import Post, Comment
from .forms import PostForm, CommentForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from api.views import PostList, CommentList
from rest_framework.response import Response

# Create your views here.
def _postHelper(posts, request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			response = PostList.as_view()(request)	# makes post call to API
			form = PostForm()						# Clear Form after posting
			# -- TODO : display post success or failure on mainStream.html -- #
			
			# print "DEBUG : post - views.py"
			# post = form.save(commit=False)
			# post.author = request.user
			# post.publish_date = timezone.now()
			# post.save()
	else:
		form = PostForm()
		response = None

	return render(request, 'post/mainStream.html', {'posts': posts, 'form':form})

def public_stream(request):
	if (request.user.is_authenticated()):
		posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
		return _postHelper(posts, request)

	else:
		return HttpResponseRedirect(reverse('accounts_login'))

def my_stream(request):
	if (request.user.is_authenticated()):
		posts = Post.objects.filter(author=request.user).order_by('-published')
		return _postHelper(posts, request)

	else:
		return HttpResponseRedirect(reverse('accounts_login'))




def _commentHelper(post, request):
	if request.method == "POST":
		commentForm = CommentForm(request.POST)
		if commentForm.is_valid():
			response = CommentList.as_view()(request, post.id)	# makes post call to API
			commentForm = CommentForm()						# Clear Form after posting
			# -- TODO : display post success or failure on post/postDetail.html -- #
			
			# print "DEBUG : post - views.py"
			# post = form.save(commit=False)
			# post.author = request.user
			# post.publish_date = timezone.now()
			# post.save()
	else:
		commentForm = CommentForm()
		response = None

	return render(request, 'post/postDetail.html', {'post': post, 'commentForm': commentForm})


def post_detail(request, post_pk):
	if (request.user.is_authenticated()):
		post = Post.objects.get(pk=post_pk)
		return _commentHelper(post, request)

	else:
		return HttpResponseRedirect(reverse('accounts_login'))