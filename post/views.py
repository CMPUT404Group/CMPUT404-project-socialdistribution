from django.shortcuts import render
from django.utils import timezone
from api.models import Post
from .forms import PostForm
from django.http import HttpResponseRedirect
# Create your views here.
def _helper(posts, request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			print "DEBUG : post - views.py"
			post = form.save(commit=False)
			post.author = request.user
			post.publish_date = timezone.now()
			post.save()
	else:
		form = PostForm()

	return render(request, 'post/mainStream.html', {'posts': posts, 'form':form })

def public_stream(request):
	if (request.user.is_authenticated()):

		posts = Post.objects.filter(privilege='PB').order_by('-publish_date')
		return _helper(posts, request)

	else:
		return HttpResponseRedirect('accounts/login')

def my_stream(request):
	if (request.user.is_authenticated()):

		posts = Post.objects.filter(author=request.user).order_by('-publish_date')
		return _helper(posts, request)

	else:
		return HttpResponseRedirect('/../accounts/login')