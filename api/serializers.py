from rest_framework import serializers
from api.models import Post
from django.contrib.auth.models import User
from django.utils import timezone

class PostSerializer(serializers.ModelSerializer):
	author = serializers.ReadOnlyField(source='author.username')
	publish_date = serializers.ReadOnlyField(default=timezone.now)
	class Meta:
		model = Post
		fields = ('id', 'title', 'content', 'publish_date', 'author', 'privilege', 'content_type')



class UserSerializer(serializers.ModelSerializer):
	# posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
	
	class Meta:
		model = User
		fields = ('id', 'username')
		# fields = ('id', 'username', 'posts')