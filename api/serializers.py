from rest_framework import serializers
from api.models import Post, Comment
from django.contrib.auth.models import User
from django.utils import timezone


class CommentSerializer(serializers.ModelSerializer):
	author = serializers.ReadOnlyField(source='author.username')
	published = serializers.ReadOnlyField(default=timezone.now)

	class Meta:
		model = Comment
		fields = ('id', 'author', 'comment', 'contentType', 'published')



class PostSerializer(serializers.ModelSerializer):
	author = serializers.ReadOnlyField(source='author.username')
	published = serializers.ReadOnlyField(default=timezone.now)
	comments = CommentSerializer(many=True, read_only=True)

	class Meta:
		model = Post
		fields = ('id', 'title', 'content', 'published', 'author', 'visibility', 'contentType', 'comments')


class UserSerializer(serializers.ModelSerializer):
	# posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
	
	class Meta:
		model = User
		fields = ('id', 'username')
		# fields = ('id', 'username', 'posts')