from rest_framework import serializers
from api.models import Post
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
	author = serializers.ReadOnlyField(source='author.username')
	class Meta:
		model = Post
		fields = ('id', 'title', 'content', 'publish_date', 'author', 'privilege', 'content_type')



class UserSerializer(serializers.ModelSerializer):
	# posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
	
	class Meta:
		model = User
		fields = ('id', 'username')
		# fields = ('id', 'username', 'posts')