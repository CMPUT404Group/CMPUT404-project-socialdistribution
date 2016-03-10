from rest_framework import serializers
<<<<<<< HEAD
from api.models import Post, Comment, Image, Author, Friend
=======
from api.models import Post, Comment, Image, Author
>>>>>>> refs/remotes/origin/master
from django.contrib.auth.models import User
from django.utils import timezone


class CommentSerializer(serializers.ModelSerializer):
	author = serializers.ReadOnlyField(source='author.username')
	published = serializers.ReadOnlyField(default=timezone.now)

	class Meta:
		model = Comment
		fields = ('id', 'author', 'comment', 'contentType', 'published')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('github_name', 'picture', 'host')


class PostSerializer(serializers.ModelSerializer):
	author = serializers.ReadOnlyField(source='author.username')
        #github_name = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
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
	author = serializers.ReadOnlyField(source='author.username')

	class Meta:
		model = Image
		fields = ('photo', 'upload_date', 'author')
<<<<<<< HEAD
=======

class AuthorSerializer(serializers.ModelSerializer):
	picture = serializers.ImageField(use_url=True)

	class Meta:
		model = Author
		fields = ('id', 'github_name', 'picture', 'host')
>>>>>>> refs/remotes/origin/master
