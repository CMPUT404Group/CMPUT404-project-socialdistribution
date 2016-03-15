from rest_framework import serializers
from api.models import Post, Comment, Image, Author, Friending
from django.contrib.auth.models import User
from django.utils import timezone


class AuthorSerializer(serializers.ModelSerializer):
	picture = serializers.ImageField(use_url=True)

	class Meta:
		model = Author
		fields = ('id', 'github_name', 'picture', 'host')

class FriendingSerializer(serializers.ModelSerializer):
	author = AuthorSerializer(read_only=True)
	friend = AuthorSerializer(read_only=True)

	class Meta:
		model = Friending
		fields = ('author', 'friend')

class CommentSerializer(serializers.ModelSerializer):
	author = AuthorSerializer(read_only=True)
	published = serializers.ReadOnlyField(default=timezone.now)

	class Meta:
		model = Comment
		fields = ('id', 'author', 'comment', 'contentType', 'published')

class PostSerializer(serializers.ModelSerializer):
	author = AuthorSerializer(read_only=True)
	published = serializers.ReadOnlyField(default=timezone.now)
	comments = CommentSerializer(many=True, read_only=True)

	class Meta:
		model = Post
		fields = ('id', 'title', 'content', 'published', 'author', 'visibility', 'contentType', 'comments', 'image_url')

class UserSerializer(serializers.ModelSerializer):
	# posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
	
	class Meta:
		model = User
		fields = ('id', 'username')
		# fields = ('id', 'username', 'posts')

class ImageSerializer(serializers.ModelSerializer):
	photo = serializers.ImageField(use_url=True)
	upload_date = serializers.ReadOnlyField(default=timezone.now)
	author = AuthorSerializer(read_only=True)

	class Meta:
		model = Image
		fields = ('photo', 'upload_date', 'author')


