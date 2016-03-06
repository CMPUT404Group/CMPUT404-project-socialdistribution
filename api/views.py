from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from api.models import Post, Comment, Upload
from api.serializers import PostSerializer, CommentSerializer
from api.serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import Http404
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import generics
from api.paginators import ListPaginator
from django.shortcuts import get_object_or_404

# Create your views here.
'''
Lists all Posts  / Create a new Post
'''
class PostList(generics.GenericAPIView):
	pagination_class = ListPaginator
	serializer_class = PostSerializer
	queryset = Post.objects.all()

	def get(self, request, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):
			posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
			page = self.paginate_queryset(posts)
			if page is not None:
				serializer = PostSerializer(page, many=True)
				return self.get_paginated_response({"data":serializer.data, "query": "posts"})
			#else:

		else:
			return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)

	def post(self, request, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):
			serializer = PostSerializer(data=request.data)
			if serializer.is_valid():
				print "DEBUG : API - views.py - PostList"
				serializer.validated_data["author"] = request.user
				serializer.validated_data["published"] = timezone.now()
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)

			else:
				Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		else:
			return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)



'''
Gets a specific Post / Updates a Post / Deletes a Post 
'''
class PostDetail(generics.GenericAPIView):
	serializer_class = PostSerializer
	queryset = Post.objects.all()

	def get_object(self, pk):
		return get_object_or_404(Post, pk=pk)


	def get(self, request, pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):

			# --- TODO : Only authorize users to read/get this post if visibility/privacy settings allow it
			post = self.get_object(pk)
			serializer = PostSerializer(post)
			return Response(serializer.data)

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

	def put(self, request, pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):
			post = self.get_object(pk)

			# only allow author of the post to modify it
			if request.user == post.author:
				serializer = PostSerializer(post, data=request.data)
				if serializer.is_valid():
					serializer.save()
					return Response(serializer.data)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			# if logged in user is not author of the post
			else:
				return Response(status=status.HTTP_403_FORBIDDEN)

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)


	def delete(self, request, pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):
			post = self.get_object(pk)
			# only allow author of the post to modify it
			if request.user == post.author:
				post.delete()
				return Response(status=status.HTTP_204_NO_CONTENT)

			# if logged in user is not author of the post
			else:
				return Response(status=status.HTTP_403_FORBIDDEN)

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)


'''
Lists all Comments for specific post  / Create a new comment
'''
class CommentList(generics.GenericAPIView):
	pagination_class = ListPaginator
	serializer_class = CommentSerializer
	queryset = Comment.objects.all()

	def get(self, request, post_pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):
			
			# --- TODO : Only authorize users to read/get this post if visibility/privacy settings allow it
			comments = Comment.objects.filter(post=post_pk).order_by('-published')
			page = self.paginate_queryset(comments)
			if page is not None:
				serializer = CommentSerializer(page, many=True)
				return self.get_paginated_response({"data":serializer.data, "query": "comments"})
			# else 

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)


	def post(self, request, post_pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):

			# -- TODO : Only authorize user who can view the corresponding post to comment
			serializer = CommentSerializer(data=request.data)
			if serializer.is_valid():
				print "DEBUG : API - views.py - CommentList"
				serializer.validated_data["author"] = request.user
				serializer.validated_data["published"] = timezone.now()
				serializer.validated_data["post"] = Post.objects.get(pk=post_pk)
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			else:
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)


'''
Gets a specific Comment/ Updates a Comment / Deletes a Comment
'''
class CommentDetail(generics.GenericAPIView):
	serializer_class = CommentSerializer
	queryset = Comment.objects.all()

	def get_object(self, pk):
		return get_object_or_404(Comment, pk=pk)


	def get(self, request, post_pk, comment_pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):

			# --- TODO : Only authorize users to read/get this comment if visibility/privacy settings of the corresponding post allow it
			comment = self.get_object(comment_pk)
			serializer = CommentSerializer(comment)
			return Response(serializer.data)

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

	def put(self, request, post_pk, comment_pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):
			comment = self.get_object(comment_pk)

			# only allow author of the comment to modify it
			if request.user == comment.author:
				serializer = CommentSerializer(post, data=request.data)
				if serializer.is_valid():
					serializer.save()
					return Response(serializer.data)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			# if logged in user is not author of the comment
			else:
				return Response(status=status.HTTP_403_FORBIDDEN)

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)


	def delete(self, request, post_pk, comment_pk, format=None):
		# ensure user is authenticated
		if (request.user.is_authenticated()):
			comment = self.get_object(comment_pk)
			# only allow author of the comment to modify it
			if request.user == comment.author:
				comment.delete()
				return Response(status=status.HTTP_204_NO_CONTENT)

			# if logged in user is not author of the comment
			else:
				return Response(status=status.HTTP_403_FORBIDDEN)

		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)



'''
Lists all Users
'''
class UserList(APIView):
	def get(self, request, format=None):
		users = User.objects.all()
		serializer = UserSerializer(users, many=True)
		return Response(serializer.data)


'''
Get a specific User
'''
class UserDetail(APIView):
	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		user = self.get_object(pk)
		serializer = UserSerializer(user)
		return Response(serializer.data)
