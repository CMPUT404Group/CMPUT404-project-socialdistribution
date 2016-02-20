from django.shortcuts import render
from django.utils import timezone
from api.models import Post
from .forms import PostForm

# Create your views here.
def public_stream(request):
	posts = Post.objects.filter(privilege='PB').order_by('date')

	form = PostForm()
	
	# if request.method == "POST":
	# 	form = PostForm(request.POST)	
	# 	if form.is_valid():
	# 		post = form.save(commit=False)
	# 		post.author = request.user
	# 		# post.author = User.objects.get(username=request.user.username)
	# 		post.publish_date = timezone.now()
	# 		post.save()
	# else:
	# 	form = PostForm()

	return render(request, 'post/mainStream.html', {'posts': posts, 'form':form })

def my_stream(request):
	posts = Post.objects.filter(author=request.user).order_by('date')
	form = PostForm()

	return render(request, 'post/mainStream.html', {'posts': posts, 'form':form })