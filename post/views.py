from django.shortcuts import render
from django.utils import timezone
from .models import Post

# Create your views here.
def public_stream(request):
	posts = Post.objects.filter(privacy='PB').order_by('date')
	return render(request, 'post/mainStream.html', {'posts': posts})