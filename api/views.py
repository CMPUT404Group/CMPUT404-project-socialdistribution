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
from api.paginators import PostPaginator

# Create your views here.
'''
Lists all Posts  / Create a new Post
'''
class PostList(generics.GenericAPIView):
	pagination_class = PostPaginator
	serializer_class = PostSerializer
	queryset = Post.objects.all()

	def get(self, request, format=None):
		posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
		page = self.paginate_queryset(posts)
		if page is not None:
			serializer = PostSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		# else 

	def post(self, request, format=None):
		serializer = PostSerializer(data=request.data)
		if serializer.is_valid():
			print "DEBUG : API - views.py - PostList"
			serializer.validated_data["author"] = request.user
			serializer.validated_data["published"] = timezone.now()
			serializer.save()

			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)



'''
Gets a specific Post / Updates a Post / Deletes a Post 
'''
class PostDetail(generics.GenericAPIView):
	serializer_class = PostSerializer
	queryset = Post.objects.all()

	def get_object(self, pk):
		try:
			return Post.objects.get(pk=pk)
		except Post.DoesNotExist:
			raise Http404


	def get(self, request, pk, format=None):
		post = self.get_object(pk)
		serializer = PostSerializer(post)
		return Response(serializer.data)


	def put(self, request, pk, format=None):
		post = self.get_object(pk)
		serializer = PostSerializer(post, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	def delete(self, request, pk, format=None):
		post = self.get_object(pk)
		post.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)




'''
Lists all Posts  / Create a new Post
'''
class CommentList(generics.GenericAPIView):
	serializer_class = CommentSerializer
	queryset = Comment.objects.all()
	
	def get(self, request, post_pk, format=None):
		comments = Comment.objects.filter(post=post_pk)
		serializer = CommentSerializer(comments, many=True)
		return Response({ "comments": serializer.data })

	def post(self, request, post_pk, format=None):
		serializer = CommentSerializer(data=request.data)
		if serializer.is_valid():
			print "DEBUG : API - views.py - CommentList"
			serializer.validated_data["author"] = request.user
			serializer.validated_data["published"] = timezone.now()
			serializer.validated_data["post"] = Post.objects.get(pk=post_pk)
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)



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
