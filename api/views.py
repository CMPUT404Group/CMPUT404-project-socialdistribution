from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from api.models import Post, Comment, Upload, Image, Following, Friending, Author
from api.serializers import PostSerializer, CommentSerializer, ImageSerializer, AuthorSerializer, FriendingSerializer, FollowingSerializer
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
from django.conf import settings
from itertools import chain
from django.conf import settings
from rest_framework.reverse import reverse

# Create your views here.
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'posts': reverse('post-list', request=request, format=format),
        'author': reverse('author-list', request=request, format=format),
      #  'images': reverse('images', request=request, format=format),
        'friends': str(request.build_absolute_uri) + '<author_id>/friends',
    })


class PostList(generics.GenericAPIView):
    '''
    Lists all Posts  / Create a new Post
    '''
    pagination_class = ListPaginator
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get(self, request, format=None):
        print request.get_host()
        print request.META.get('REMOTE_ADDR')  
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = PostSerializer(page, many=True)
                return self.get_paginated_response({"data": serializer.data, "query": "posts"})
                # else:

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, post_pk=None, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            if post_pk != None:
                post = get_object_or_404(Post, pk=post_pk)
                # only allow author of the post to modify it
                author = Author.objects.get(user=request.user)
                if author == post.author:
                    serializer = PostSerializer(post, data=request.data)
                # if logged in user is not author of the post
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            else:
                serializer = PostSerializer(data=request.data)

            if serializer.is_valid():
                print "DEBUG : API - views.py - PostList"
                serializer.validated_data["author"] = Author.objects.get(user=request.user)
                serializer.validated_data["published"] = timezone.now()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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

    def isAllowed(self,request,pk):
        post = Post.objects.get(id=pk)
        privacy = post.visibility
        viewer = Author.objects.get(user=request.user)

        #if the post was created by the user allow access
        if viewer == post.author :
            return True
        #if it is a public post allow everypne access
        elif privacy == "PUBLIC":
            return True
        #check if the user is in the friend list
        elif privacy == "FRIENDS" or privacy == "FOAF":
            friend_pairs = Friending.objects.filter(author=post.author)
            friends = []
            for i in range(len(friend_pairs)):
                friends.append(friend_pairs[i].friend)
            if viewer in friends:
                return True
            #check if the user is in the FoaF list
            elif privacy == "FOAF":
                for i in range(len(friends)):
                    fofriend_pairs = Friending.objects.filter(author=friends[i])
                    fofriends = []
                    for i in range(len(fofriend_pairs)):
                        fofriends.append(fofriend_pairs[i].friend)
                    if viewer in fofriends:
                        return True
            #if not a friend return false
            else:
                return False
        else:
            return False


    def get(self, request, pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            if (self.isAllowed(request,pk)):
                post = self.get_object(pk)
                serializer = PostSerializer(post)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            post = self.get_object(pk)

            # only allow author of the post to modify it
            if Author.objects.get(user=request.user) == post.author:
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
            if Author.objects.get(user=request.user)== post.author:
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

    def isAllowed(self,request,pk):
        post = Post.objects.get(id=pk)
        privacy = post.visibility
        viewer = Author.objects.get(user=request.user)

        #if the post was created by the user allow access
        if viewer == post.author :
            return True
        #if it is a public post allow everypne access
        elif privacy == "PUBLIC":
            return True
        #check if the user is in the friend list
        elif privacy == "FRIENDS" or privacy == "FOAF":
            friend_pairs = Friending.objects.filter(author=post.author)
            friends = []
            for i in range(len(friend_pairs)):
                friends.append(friend_pairs[i].friend)
            if viewer in friends:
                return True
            #check if the user is in the FoaF list
            elif privacy == "FOAF":
                for i in range(len(friends)):
                    fofriend_pairs = Friending.objects.filter(author=friends[i])
                    fofriends = []
                    for i in range(len(fofriend_pairs)):
                        fofriends.append(fofriend_pairs[i].friend)
                    if viewer in fofriends:
                        return True
            #if not a friend return false
            else:
                return False
        else:
            return False

    def get(self, request, post_pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            # --- TODO : Only authorize users to read/get this post if visibility/privacy settings allow it
            if(self.isAllowed(request, post_pk)):
                comments = Comment.objects.filter(post=post_pk).order_by('-published')
                page = self.paginate_queryset(comments)
                if page is not None:
                    serializer = CommentSerializer(page, many=True)
                    return self.get_paginated_response({"data": serializer.data, "query": "comments"})
                # else
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, post_pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):

            # -- TODO : Only authorize user who can view the corresponding post to comment
            if(self.isAllowed(request,post_pk)):
                serializer = CommentSerializer(data=request.data)
                if serializer.is_valid():
                    print "DEBUG : API - views.py - CommentList"
                    serializer.validated_data["author"] = Author.objects.get(user=request.user)
                    serializer.validated_data["published"] = timezone.now()
                    serializer.validated_data["post"] = Post.objects.get(pk=post_pk)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
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

    def isAllowed(self,request,pk):
        post = Post.objects.get(id=pk)
        privacy = post.visibility
        viewer = Author.objects.get(user=request.user)

        #if the post was created by the user allow access
        if viewer == post.author :
            return True
        #if it is a public post allow everypne access
        elif privacy == "PUBLIC":
            return True
        #check if the user is in the friend list
        elif privacy == "FRIENDS" or privacy == "FOAF":
            friend_pairs = Friending.objects.filter(author=post.author)
            friends = []
            for i in range(len(friend_pairs)):
                friends.append(friend_pairs[i].friend)
            if viewer in friends:
                return True
            #check if the user is in the FoaF list
            elif privacy == "FOAF":
                for i in range(len(friends)):
                    fofriend_pairs = Friending.objects.filter(author=friends[i])
                    fofriends = []
                    for i in range(len(fofriend_pairs)):
                        fofriends.append(fofriend_pairs[i].friend)
                    if viewer in fofriends:
                        return True
            #if not a friend return false
            else:
                return False
        else:
            return False

    def get_object(self, pk):
        return get_object_or_404(Comment, pk=pk)

    def get(self, request, post_pk, comment_pk, format=None):
        print comment_pk
        # ensure user is authenticated
        if (request.user.is_authenticated()):

            # --- TODO : Only authorize users to read/get this comment if visibility/privacy settings of the corresponding post allow it
            if(self.isAllowed(request,post_pk)):
                print "IN HERE"
                comment = self.get_object(comment_pk)
                print "OU HERE"
                serializer = CommentSerializer(comment)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, post_pk, comment_pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            comment = self.get_object(comment_pk)

            # only allow author of the comment to modify it
            if Author.objects.get(user=request.user) == comment.author:
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
            if Author.objects.get(user=request.user) == comment.author:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            # if logged in user is not author of the comment
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


'''
Uploads a new image
'''


class Images(generics.GenericAPIView):
    # pagination_class = ListPaginator
    serializer_class = ImageSerializer

    # queryset = Post.objects.all()

    # def get(self, request, format=None):
    # 	# ensure user is authenticated
    # 	if (request.user.is_authenticated()):
    # 		posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
    # 		page = self.paginate_queryset(posts)
    # 		if page is not None:
    # 			serializer = PostSerializer(page, many=True)
    # 			return self.get_paginated_response({"data":serializer.data, "query": "posts"})
    # 		#else:

    # 	else:
    # 		return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            serializer = ImageSerializer(data=request.data)

            if serializer.is_valid():
                print "DEBUG : API - views.py - Images"
                serializer.validated_data["author"] = Author.objects.get(user=request.user)
                serializer.validated_data["upload_date"] = timezone.now()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        # def perform_create(self, serializer):
        # 	serializer.save(author=self.request.user)


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

''' Author List '''
class AuthorList(generics.GenericAPIView):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()

    def get(self, request,format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            authors = Author.objects.all()
            serializer = AuthorSerializer(authors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

''' Gets Author / Updates Author via POST '''
class AuthorDetail(generics.GenericAPIView):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()

    def get_object(self, pk):
        return get_object_or_404(Author, pk=pk)

    def get(self, request, author_pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):

            author = self.get_object(author_pk)
            serializer = AuthorSerializer(author)

            # get the author's friend list
            responseData = serializer.data
            friendsList = []
            # return json object so we must extract the friend
            aList = Friending.objects.filter(author=author).select_related('friend')
            friendsList = []
            for i in aList:
                friendsList.append(i.friend)
            serializer = AuthorSerializer(friendsList, many=True)
            responseData["friends"] = serializer.data

            responseData["url"] = author.host + "author/" + author.user.username

            return Response(responseData, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, author_pk=None, format=None):
        if (request.user.is_authenticated()):

            # update profile picture only
            if (request.data["github_name"] == "" and request.data['host'] == "" and request.data["picture"] != ""):
                author = get_object_or_404(Author, pk=author_pk)
                if request.user == author.user:
                    author.picture = request.data["picture"]
                    author.save()
                    serializer = AuthorSerializer(author)
                    print serializer
                    print serializer.data
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                   return Response(status=status.HTTP_403_FORBIDDEN)

            # Haven't tested this part below yet
            else:   
                if author_pk != None:
                    author = get_object_or_404(Author, pk=author_pk)
                    # only allow author of the post to modify it
                    if request.user == author.user:
                        #serializer = AuthorSerializer(author, data=request.data)
                    # if logged in user is not author of the post
                    else:
                        return Response(status=status.HTTP_403_FORBIDDEN)
                else:
                    serializer = AuthorSerializer(data=request.data)

                if serializer.is_valid():
                    print "DEBUG : API - views.py - AuthorDetail"
                    # serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                else:
                    Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



class FriendingCheck(generics.GenericAPIView):
    queryset = Friending.objects.all()
    serializer_class = FriendingSerializer

    def get(self, request, author_id1, author_id2=None, format=None):
        if request.user.is_authenticated():

            # returns whether or not author_id1 & author_id2 are friends or not
            if author_id2 != None:
                aList = Friending.objects.filter(author__id=author_id1, friend__id=author_id2)
                bList = Friending.objects.filter(author__id=author_id2, friend__id=author_id1)
                result = list(chain(aList, bList))
                print result
                if (result != []):
                    friends = True
                else:
                    friends = False
                return Response({'query':'friends', 'authors': [author_id1, author_id2], 'friends':friends}, status=status.HTTP_200_OK)
            

            # returns all friends of author_1
            else:
                friendsList = []
                # return json object so we must extract the friend id
                aList = Friending.objects.filter(author__id=author_id1).values('friend__id')
                for i in aList:
                    friendsList.append(i["friend__id"])
                print friendsList
                return Response({'query':'friends', 'authors': friendsList}, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



class RequestList(generics.GenericAPIView):
    serializer_class = FollowingSerializer
    queryset = Following.objects.all()

    def get(self, request, author_id1, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
	    # return all auother_ids who author_id1 are following
            if author_id1 is not None:
		followerList = []
		aList = Following.objects.filter(following__id=author_id1).values('author__id')
		for i in aList:
		    followerList.append(i["author__id"])
		return Response({'query':'following', 'followers':followerList}, status=status.HTTP_200_OK)
	else:
	    return Response(status=status.HTTP_401_UNAUTHORIZED)


class FriendRequest(generics.GenericAPIView):
    serializer_class = FollowingSerializer
    queryset = Following.objects.all()

    def post(self, request, format=None):
	# if (request.user.is_authenticated()):
	    if request.data is not None:

		authorid = request.data["author"]["id"]
		followid = request.data["friend"]["id"] 
		
#		author1 = Author.objects.get(id=authorid)
#		follow1 = Author.objects.get(id=friendid)
#		try:
#		    Author.objects.get(id=author1)
#		    Author.objects.get(id=friend1)
#		except:
#		    return Response(status=status.HTTP_400_BAD_REQUEST)
		serializer = FollowingSerializer(data=request.data)
		if serializer.is_valid():
		    serializer.validated_data["author"] = Author.objects.get(id=authorid)
		    serializer.validated_data["following"] = Author.objects.get(id=followid)
		    serializer.save()
		    return Response(serializer.data, status=status.HTTP_201_CREATED)
	# else:
	#    return Response(status=status.HTTP_401_UNAUTHORIZED)


class BeFriend(generics.GenericAPIView):
    serializer_class = FriendingSerializer
    queryset = Friending.objects.all()

    def post(self, request, format=None):
	# if (request.user.is_authenticated()):
	    if request.data is not None:

		authorid = request.data["author"]["id"]
		friendid = request.data["friend"]["id"] 
		
#		author1 = Author.objects.get(id=authorid)
#		follow1 = Author.objects.get(id=friendid)
#		try:
#		    Author.objects.get(id=author1)
#		    Author.objects.get(id=friend1)
#		except:
#		    return Response(status=status.HTTP_400_BAD_REQUEST)
		serializer = FriendingSerializer(data=request.data)
		if serializer.is_valid():
		    serializer.validated_data["author"] = Author.objects.get(id=authorid)
		    serializer.validated_data["friend"] = Author.objects.get(id=friendid)
		    serializer.save()
		    return Response(serializer.data, status=status.HTTP_201_CREATED)
	# else:
	#    return Response(status=status.HTTP_401_UNAUTHORIZED)



