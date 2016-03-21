from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from api.models import Post, Comment, Image, Friending, Author, Node
from api.serializers import PostSerializer, CommentSerializer, ImageSerializer, AuthorSerializer, FriendingSerializer
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
from post.models import Notification
import json
import urllib2
import json
import base64
from rest_framework import HTTP_HEADER_ENCODING

# Create your views here.
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'posts': reverse('post-list', request=request, format=format),
        'author': reverse('author-list', request=request, format=format),
        'images': reverse('images', request=request, format=format),
        'friendrequest': reverse('friendrequest', request=request, format=format),
    })


'''
Paramters:
    * Post_pk - the post whose privacy / visibility settings is being checked
    * Author_id - author who is wants to view the post
Return:
    * True if access is allowed, False otherwise
'''
def isAllowed(post_pk, author_id):
    try:
        post = Post.objects.get(id=post_pk)
    except:
        raise Post.DoesNotExist

    if post.visibility == Post.PUBLIC:
        return True
    
    privacy = post.visibility
    viewer = Author.objects.get(id=author_id)

    #if the post was created by the user allow access
    if viewer == post.author :
        return True
    #if it is a public post allow everypne access
    elif privacy == Post.PUBLIC:
        return True
    elif privacy == Post.SERVER_ONLY:
        if viewer.host == post.author.host:
            return True
        else:
            return False
    #checks if another post is being shared with you
    elif privacy == Post.OTHER_AUTHOR:
        user = User.objects.get(username=post.other_author)
        other_author = Author.objects.get(user=user)
        if other_author.id == author_id:
            return True
        else:
            return False
    #check if the user is in the friend list
    elif privacy == Post.FRIENDS or privacy == Post.FRIENDS_OF_FRIENDS:
        friend_pairs = Friending.objects.filter(author=post.author)
        friends = []
        for i in range(len(friend_pairs)):
            #make sure they are mutual friends
            backwards = Friending.objects.filter(author=friend_pairs[i].friend,friend=post.author)
            if len(backwards) > 0:
                friends.append(friend_pairs[i].friend)
        if viewer in friends:
            return True
        #check if the user is in the FoaF list
        elif privacy == Post.FRIENDS_OF_FRIENDS:
            for i in range(len(friends)):
                fofriend_pairs = Friending.objects.filter(author=friends[i])
                fofriends = []
                for j in range(len(fofriend_pairs)):
                    #make sure they are mutual friends
                    backwards = Friending.objects.filter(friend=friends[i],author=fofriend_pairs[j].friend)
                    if len(backwards) > 0:
                        fofriends.append(fofriend_pairs[j].friend)
                if viewer in fofriends:
                    return True
        #if not a friend return false
        else:
            return False
    else:
        return False


'''
Parameters : 
    * author_id
Return:
    * list of all friends (list of Author ids)
'''
def getAllFriends(author_id):
    friendsList = []
    # return json object so we must extract the friend id
    aList = Friending.objects.filter(author__id=author_id).values('friend__id')
    for i in aList:
        # if both people are following eachother (so two-way friendship)
        blist = Friending.objects.filter(author__id=i["friend__id"], friend__id=author_id)
        if len(blist) > 0:
            friendsList.append(i["friend__id"])
    return friendsList


'''
Parameters : 
    * author_id
Return:
    * list of all friends of friends (list of Author ids) - no duplicates
'''
def getAllFOAF(author_id):
    friends = getAllFriends(author_id)
    foaf = []
    for friend_id in friends:
        tempFofs = getAllFriends(friend_id)
        newFriends = list(set(tempFofs) - set(foaf))
        foaf.extend(newFriends)
    return foaf

def getRemoteAuthorProfile(node_url, request):
    url = node_url + 'api/author/' + request.META.get("HTTP_REMOTE_USER")
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(url)

    credentials = { "http://project-c404.rhcloud.com/" : "team4:team4team4",\
                    "http://disporia-cmput404.rhcloud.com/": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ"}
    print node_url
    print url
    # set credentials on request
    if node_url == "http://project-c404.rhcloud.com/":
        creds = base64.b64encode(credentials["node_url"])
        req.add_header("Authorization", "Basic " + creds)
    elif node_url == "http://disporia-cmput404.rhcloud.com/":
        creds = credentials["node_url"]
        req.add_header("Authorization", "JWT " + creds)

    # # fill this with OUR authentication credentials provided by OTHER TEAMS
    # encodedValue = base64.b64encode("nodeHost4B@nodeHost4B:host4b")

    # # do basic auth
    # request.add_header("Authorization", "Basic " + encodedValue ) #Header, Value 

    x = opener.open(req)
    y = x.read()

    author_serializer = AuthorSerializer(json.loads(y))

    print author_serializer.data
    return author_serializer

''' 
Returns True if request.user is a Node
Returns False if request.user is an Author
'''
def getRemoteNode(user):
    try:
        node = Node.objects.get(user=user)
        # print node
        # print node.hostname,
        # print " - ",
        # print node.url
        return node
    except Node.DoesNotExist as e:
        return None

class PostList(generics.GenericAPIView):
    '''
    Lists all Posts  |  Create a new Post / Update an existing post

    GET : http://service/api/posts/ 
        * Returns a list of all public posts on the server - most recent to least recent order

    POST : http://service/api/posts/
        * Creates a new post

    POST : http://service/api/posts/<post_pk>
        * Updates the post specified by the post_pk

    '''
    pagination_class = ListPaginator
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get(self, request, format=None):
        posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
        page = self.paginate_queryset(posts)
        serializer = PostSerializer(page, many=True)
        return self.get_paginated_response({"data": serializer.data, "query": "posts"})


    def post(self, request, post_pk=None, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data

        '''
        Gets the author from the request
        '''
        try:
            author = Author.objects.get(user=request.user)
        except Author.DoesNotExist as e:
            return Response({"message":"Author does not exist / is not a local author"}, status=status.HTTP_400_BAD_REQUEST)

        # If its a remote node - not allowed to make posts
        if request.get_host() not in author.host:
            return Response({"message":"Only local authors can make posts"}, status=status.HTTP_403_FORBIDDEN)


        statusCode = status.HTTP_201_CREATED

        '''
        Handles : EDIT Posts via POST method
        '''
        if post_pk != None:
            try:
                post = Post.objects.get(id=post_pk)
            except Post.DoesNotExist as e:
                return Response({"message": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND)


            # only allow author of the post to modify it
            if author != post.author:
                return Response({"message":"Only the author of this post can make changes to it"}, status=status.HTTP_403_FORBIDDEN)

            statusCode = status.HTTP_200_OK



        serializer = PostSerializer(data=data)

        if serializer.is_valid():
            print "DEBUG : API - views.py - PostList"
            serializer.validated_data["author"] = author
            serializer.validated_data["published"] = timezone.now()
            serializer.save()
            return Response(serializer.data, status=statusCode)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(generics.GenericAPIView):

    '''
    Gets a specific Post / Updates a Post / Deletes a Post 

    GET : http://service/api/posts/<post_pk> 
        * Returns the post with id post_pk

    PUT : http://service/api/posts/<post_pk>
        * Updates the post specified at post_pk

    DELETE : http://service/api/posts/<post_pk>
        * Deletes the post specified by the post_pk

    '''

    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get(self, request, pk, format=None):
        # Returns post if it's privacy setting is public - no need to be authenticated
        # returns 404 if post does not exist
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if post.visibility == Post.PUBLIC:
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)



        # if post is not public - ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


        '''
        Gets the author from the request
        '''
        try:
            author = Author.objects.get(user=request.user)

        except Author.DoesNotExist as e:
            # check if it is a remote node
            remoteNode = getRemoteNode(request.user)

            # not a remote author & not a local author
            if remoteNode == None:
                return Response({"message":"Node not allowed"},status=status.HTTP_403_FORBIDDEN)

            # is a remote author - assume remote author is already authenticated by remote node
            author_id = request.META.get("HTTP_REMOTE_USER")
            if (isAllowed(pk, author_id)):
                serializer = PostSerializer(post)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response({"message": "User is not allowed to see this post"}, status=status.HTTP_403_FORBIDDEN)
       
       # If its a local author - return the post
        if request.get_host() in author.host:
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # check if it is a remote node
        remoteNode = getRemoteNode(request.user)

        # not a remote author & not a local author
        if remoteNode == None:
            return Response({"message":"Node not allowed"},status=status.HTTP_403_FORBIDDEN)

        # is a remote author - assume remote author is already authenticated by remote node
        author_id = request.META.get("HTTP_REMOTE_USER")
        author_serializer = getRemoteAuthorProfile(remoteNode.url, request)
        # get remoteAuthor's Author object in our database (has id, displayname, host only - no user) if we already have it
        # else, create a new author object w/o user
        # author = remoteAuthor here
        try:
            author = Author.objects.get(id=author_serializer.data["id"])
        except Author.DoesNotExist as e:
            author = Author.objects.create(id=author_serializer.data["id"], displayname=author_serializer.data["displayname"], host=remoteNode.url)
            author.save()

        if (isAllowed(pk, author_id)):
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"message": "User is not allowed to see this post"}, status=status.HTTP_403_FORBIDDEN)
       
    def put(self, request, pk, format=None):
        data = request.data

        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # only allow author of the post to modify it
        try:
            loggedInAuthor = Author.objects.get(user=request.user)
        except Author.DoesNotExist as e:
            return Response({"message":"Author does not exist"}, status=status.HTTP_401_UNAUTHORIZED)

        # only allow author of the post to modify it
        if loggedInAuthor != post.author:
            return Response({"message": "User is not the author of this post & is not allowed to update this post"}, status=status.HTTP_403_FORBIDDEN)


        # else logged in user is the author of the post
        serializer = PostSerializer(post, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            loggedInAuthor = Author.objects.get(user=request.user)
        except Author.DoesNotExist as e:
            return Response({"message":"Author does not exist"}, status=status.HTTP_401_UNAUTHORIZED)

        # only allow author of the post to delete it
        if loggedInAuthor != post.author:
            return Response({"message": "User is not the author of this post & is not allowed to delete this post"}, status=status.HTTP_403_FORBIDDEN)

        # else if logged in user is author of the post, delete it
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentList(generics.GenericAPIView):
    '''
    Lists all Comments for specific post  / Create a new comment

    GET : http://service/api/posts/<post_pk>/comments/
        * Returns a list of all comments on the post specified by post_pk - most recent to least recent order

    POST : http://service/api/posts/<post_pk>/comments/
        * Creates a new comment attached to the post specified by post_pk

    '''
    pagination_class = ListPaginator
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get(self, request, post_pk, format=None):
        # Returns post if it's privacy setting is public - no need to be authenticated
        # returns 404 if post does not exist
        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if post.visibility == Post.PUBLIC:
            comments = Comment.objects.filter(post=post_pk).order_by('-published')
            page = self.paginate_queryset(comments)
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response({"data": serializer.data, "query": "comments"})



        # if post is not public - ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


        # check if request is from remote node, if so handle it
        remoteNode = getRemoteNode(request.user)
        if remoteNode != None:
            author_serializer = getRemoteAuthorProfile(remoteNode.url, request)
            # get remoteAuthor's Author object in our database (has id, displayname, host only - no user) if we already have it
            # else, create a new author object w/o user
            # author = remoteAuthor here
            try:
                author = Author.objects.get(id=author_serializer.data["id"])
            except Author.DoesNotExist as e:
                author = Author.objects.create(id=author_serializer.data["id"], displayname=author_serializer.data["displayname"], host=remoteNode.url)
                author.save()

        # local author - get from db
        else:
            author  = Author.objects.get(user=request.user)


        author_id = author.id
        try:
            if (isAllowed(post_pk, author_id)):
                comments = Comment.objects.filter(post=post_pk).order_by('-published')
                page = self.paginate_queryset(comments)
                serializer = CommentSerializer(page, many=True)
                return self.get_paginated_response({"data": serializer.data, "query": "comments"})
            else:
                return Response({"message": "User is not allowed to see this comment or it's corresponding post"}, status=status.HTTP_403_FORBIDDEN)

        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request, post_pk, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data

        # check if request is from remote node, if so handle it
        remoteNode = getRemoteNode(request.user)
        if remoteNode != None:
            author_serializer = getRemoteAuthorProfile(remoteNode.url, request)
            # get remoteAuthor's Author object in our database (has id, displayname, host only - no user) if we already have it
            # else, create a new author object w/o user
            # author = remoteAuthor here
            try:
                author = Author.objects.get(id=author_serializer.data["id"])
            except Author.DoesNotExist as e:
                author = Author.objects.create(id=author_serializer.data["id"], displayname=author_serializer.data["displayname"], host=remoteNode.url)
                author.save()

        # local author - get from db
        else:
            author  = Author.objects.get(user=request.user)


        author_id = author.id
        try:
            if (isAllowed(post_pk, author_id)):
                serializer = CommentSerializer(data=data)

                if serializer.is_valid():
                    print "DEBUG : API - views.py - CommentList"
                    serializer.validated_data["author"] = author
                    serializer.validated_data["published"] = timezone.now()
                    serializer.validated_data["post"] = Post.objects.get(pk=post_pk)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({"message": "User is not allowed to see this post/comment"}, status=status.HTTP_403_FORBIDDEN)
        
        except Post.DoesNotExist as e:
            return Response({"message":"Corresponding post does not exist"}, status=status.HTTP_404_NOT_FOUND)



class CommentDetail(generics.GenericAPIView):
    '''
    Gets a specific Comment/ Updates a Comment / Deletes a Comment

    GET : http://service/api/posts/<post_pk>/comments/<comment_pk>
        * Returns the comment with id comment_pk correlating to the post specified by post_pk

    PUT : http://service/api/posts/<post_pk>/comments/<comment_pk>
        * Updates the comment specified at comment_pk

    DELETE : http://service/api/posts/<post_pk>/comments/<comment_pk>
        * Deletes the comment specified by the comment_pk

    '''
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


    def get(self, request, post_pk, comment_pk, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


        # check if request is from remote node, if so handle it
        remoteNode = getRemoteNode(request.user)
        if remoteNode != None:
            author_serializer = getRemoteAuthorProfile(remoteNode.url, request)
            # get remoteAuthor's Author object in our database (has id, displayname, host only - no user) if we already have it
            # else, create a new author object w/o user
            # author = remoteAuthor here
            try:
                author = Author.objects.get(id=author_serializer.data["id"])
            except Author.DoesNotExist as e:
                author = Author.objects.create(id=author_serializer.data["id"], displayname=author_serializer.data["displayname"], host=remoteNode.url)
                author.save()

        # local author - get from db
        else:
            author  = Author.objects.get(user=request.user)


        author_id = author.id
        try:
            if (isAllowed(post_pk, author_id)):
                comment = Comment.objects.get(id=comment_pk)
                serializer = CommentSerializer(comment)
                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                return Response({"message": "User is not allowed to see this comment or it's corresponding post"}, status=status.HTTP_403_FORBIDDEN)

        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

        except Comment.DoesNotExist as e:
            return Response({"message":"Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # need to fix
    def put(self, request, post_pk, comment_pk, format=None):
        data = request.data

        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)


        try:
            comment = Comment.objects.get(id=comment_pk)
        except Comment.DoesNotExist as e:
            return Response({"message":"Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            loggedInAuthor = Author.objects.get(user=request.user)
        except Author.DoesNotExist as e:
            return Response({"message":"Author does not exist"}, status=status.HTTP_401_UNAUTHORIZED)


        # only allow author of the comment to modify it
        if loggedInAuthor != comment.author:
            return Response({"message": "User is not the author of this comment & is not allowed to update this comment"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_pk, comment_pk, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist as e:
            return Response({"message":"Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            comment = Comment.objects.get(id=comment_pk)
        except Comment.DoesNotExist as e:
            return Response({"message":"Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            loggedInAuthor = Author.objects.get(user=request.user)
        except Author.DoesNotExist as e:
            return Response({"message":"Author does not exist"}, status=status.HTTP_401_UNAUTHORIZED)


        # only allow author of the comment to delete it
        if loggedInAuthor != comment.author:
            return Response({"message": "User is not the author of this comment & is not allowed to delete this comment"}, status=status.HTTP_403_FORBIDDEN)

        # else if logged in user is author of the comment, delete it
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class Images(generics.GenericAPIView):
    '''
    Lists all Images / Posts a new image

    GET : http://service/api/images/
        * Returns a list of all images on the server (not including profile pictures) - most recent to least recent order

    POST : http://service/api/images/
        * Creates a new image

    '''
    pagination_class = ListPaginator
    serializer_class = ImageSerializer

    queryset = Image.objects.all()

    def get(self, request, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        images = Image.objects.order_by('-upload_date')
        page = self.paginate_queryset(images)
        if page is not None:
            serializer = ImageSerializer(page, many=True)
            return self.get_paginated_response({"data":serializer.data, "query": "images"})
        #else:


    def post(self, request, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ImageSerializer(data=request.data)

        if serializer.is_valid():
            print "DEBUG : API - views.py - Images"
            serializer.validated_data["author"] = Author.objects.get(user=request.user)
            serializer.validated_data["upload_date"] = timezone.now()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AuthorList(generics.GenericAPIView):
    '''
    Lists all Authors / Posts a new Author

    GET : http://service/api/author/
        * Returns a list of authors on the server

    '''
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()

    def get(self, request,format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthorTimeline(generics.GenericAPIView):
    '''
    Lists all Posts an author has made

    GET : http://service/api/author/<author_id>/posts
        * Returns a list of all posts on the server made by author specified by <author_id> - most recent to least recent order

    '''
    pagination_class = ListPaginator
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get(self, request, author_pk=None, format=None):
        if request.user.is_authenticated():
            # get currently logged in user
            try:
                viewer = Author.objects.get(user=request.user)
            except DoesNotExist as e:
                return Response(status=status.HTTP_404_NOT_FOUND)

            # posts that are visible to the currently authenticated user
            if author_pk == None:
                # get author's own posts
                authorsPosts = Post.objects.filter(author=viewer)

                # get public posts
                publicPosts = Post.objects.filter(visibility=Post.PUBLIC)

                # get friends posts
                friends = getAllFriends(viewer.id)
                friendsPosts = Post.objects.filter(author__id__in=friends, visibility__in=[Post.FRIENDS, Post.FRIENDS_OF_FRIENDS])

                # get foaf posts
                foaf = getAllFOAF(viewer.id)
                foafPosts = Post.objects.filter(author__id__in=foaf, visibility__in=Post.FRIENDS_OF_FRIENDS)

                # combine all posts into one list w/o duplicates
                result = list(set(authorsPosts) | set(publicPosts) | set(friendsPosts) | set(foafPosts))

                # put posts in order from most recent to least recent
                resultPosts = Post.objects.filter(id__in=[post.id for post in result]).order_by('-published')

                page = self.paginate_queryset(resultPosts)
                if page is not None:
                    serializer = PostSerializer(page, many=True)
                    return self.get_paginated_response({"data": serializer.data, "query": "posts"})
                # else : TODO

            # author pk is provided - all posts made by {AUTHOR_ID} visible to the currently authenticated user
            else:   # author_pk != None
                # ensure author exists
                try:
                    viewee = Author.objects.get(id=author_pk)
                except Author.DoesNotExist as e:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                # if viewer is viewee, show all of their posts
                if (viewee.id == viewer.id):
                    resultPosts = Post.objects.filter(author=viewee).order_by('-published')

                else:
                    # get all viewee's friends & foafs
                    friends = getAllFriends(viewee.id)
                    foaf = getAllFOAF(viewee.id)

                    friendsPosts = []
                    foafPosts = []

                    # if viewer is friends or foafs with viewee, get their posts
                    if (viewer.id in friends):
                        friendsPosts = Post.objects.filter(author=viewee, visibility__in=[Post.FRIENDS, Post.FRIENDS_OF_FRIENDS])
                    if (viewer.id in foaf):
                        foafPosts = Post.objects.filter(author=viewee, visibility=Post.FRIENDS_OF_FRIENDS)

                    # viewee's public posts
                    publicPosts = Post.objects.filter(author=viewee, visibility=Post.PUBLIC)

                    # combine all posts into one list w/o duplicates
                    result = list(set(publicPosts) | set(friendsPosts) | set(foafPosts))

                    # put posts in order from most recent to least recent
                    resultPosts = Post.objects.filter(id__in=[post.id for post in result]).order_by('-published')

                page = self.paginate_queryset(resultPosts)
                if page is not None:
                    serializer = PostSerializer(page, many=True)
                    return self.get_paginated_response({"data": serializer.data, "query": "posts"})
                # else : TODO


        # only show posts by author_pk that are public - b/c user (viewer) is not logged in
        else:
            posts = Post.objects.filter(visibility=Post.PUBLIC).order_by('-published')
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = PostSerializer(page, many=True)
                return self.get_paginated_response({"data": serializer.data, "query": "posts"})
            # else : TODO


        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class AuthorDetail(generics.GenericAPIView):
    '''
    Gets Author / Updates Author via POST

    GET : http://service/api/author/<author_id>
        * Returns the author specified by author_id. This includes the author's id, github name, profile picture url, and host.

    POST : http://service/api/author/<author_id>
        * Updates the author specified by author_id

    '''
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()

    def get(self, request, author_pk, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            author = Author.objects.get(id=author_pk)
        except Author.DoesNotExist as e:
            return Response({"message":"Author does not exist"}, status=status.HTTP_404_NOT_FOUND)


        # # remote author
        # if request.get_host() not in author.host:
        #     return Response({"message": "This author is not on this node. It is a remote author on another node."}, status=status.HTTP_404_NOT_FOUND)
        
        # else local author
        serializer = AuthorSerializer(author)

        # get the author's friend list
        responseData = serializer.data
        friendsList = []
        # return json object so we must extract the friend
        aList = Friending.objects.filter(author=author)
        # friendsList = getAllFriends(author.id)
        for person_pair in aList:
            # backwards check
            if len(Friending.objects.filter(author=person_pair.friend, friend=author)) > 0:
                friendsList.append(person_pair.friend)
        serializer = AuthorSerializer(friendsList, many=True)
        responseData["friends"] = serializer.data

        if request.get_host() not in author.host:
            responseData["url"] = author.host + 'author/' + str(author.id)
        else:
            responseData["url"] = author.host + "author/" + author.user.username

        return Response(responseData, status=status.HTTP_200_OK)



    def post(self, request, author_pk=None, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            author = Author.objects.get(id=author_pk)
        except Author.DoesNotExist as e:
            return Response({"message":"Author does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if request.user == author.user:
            print "1"
            serializer = AuthorSerializer(author, data=request.data)
            print "2"  
            if serializer.is_valid():
                print "DEBUG : API - views.py - AuthorDetail"
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
           return Response({"message":"only this author can make changes to their profile"},status=status.HTTP_403_FORBIDDEN)


class FriendingCheck(generics.GenericAPIView):
    '''
    Returns a list of an author's friends / Checks whether or not 2 authors are friends

    GET : http://service/api/friends/<author_id>
        * Returns the author specified by author_id's list of friends (by friend id)

    GET : http://service/api/friends/<author_id1>/<author_id2>
        * Returns the 2 author's ids & a boolean specifying if the 2 authors are friends or not.

    '''
    queryset = Friending.objects.all()
    serializer_class = FriendingSerializer

    def get(self, request, author_id1, author_id2=None, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


        # returns whether or not author_id1 & author_id2 are friends or not
        if author_id2 != None:
            aList = Friending.objects.filter(author__id=author_id1, friend__id=author_id2)
            bList = Friending.objects.filter(author__id=author_id2, friend__id=author_id1)
            result = list(chain(aList, bList))
            if len(result) > 1:
                friends = True
            else:
                friends = False
            return Response({'query':'friends', 'authors': [author_id1, author_id2], 'friends':friends}, status=status.HTTP_200_OK)
        

        # returns all friends of author_1
        else:

            # check if request is from remote node, if so handle it
            remoteNode = getRemoteNode(request.user)
            if remoteNode != None:
                return Response({"message":"This is a remote user on another node, to see their friends, use the api of the remote user's original node"}, status=status.HTTP_400_BAD_REQUEST)
                # author_serializer = getRemoteAuthorProfile(remoteNode.url, request)
                # # get remoteAuthor's Author object in our database (has id, displayname, host only - no user) if we already have it
                # # else, create a new author object w/o user
                # # author = remoteAuthor here
                # try:
                #     author = Author.objects.get(id=author_serializer.data["id"])
                # except Author.DoesNotExist as e:
                #     author = Author.objects.create(id=author_serializer.data["id"], displayname=author_serializer.data["displayname"], host=remoteNode.url)
                #     author.save()

            # local author - get from db
            else:
                author  = Author.objects.get(user=request.user)

            author_id = author.id
            friendsList = getAllFriends(author_id)
            return Response({'query':'friends', 'authors': friendsList}, status=status.HTTP_200_OK)

    def post(self, request, author_id1, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # check if request is from remote node, if so handle it
        remoteNode = getRemoteNode(request.user)
        if remoteNode != None:
            return Response({"message":"This is a remote user on another node, to use this service, use the api of the remote user's original node"}, status=status.HTTP_400_BAD_REQUEST)
            # author_serializer = getRemoteAuthorProfile(remoteNode.url, request)
            # # get remoteAuthor's Author object in our database (has id, displayname, host only - no user) if we already have it
            # # else, create a new author object w/o user
            # # author = remoteAuthor here
            # try:
            #     author = Author.objects.get(id=author_serializer.data["id"])
            # except Author.DoesNotExist as e:
            #     author = Author.objects.create(id=author_serializer.data["id"], displayname=author_serializer.data["displayname"], host=remoteNode.url)
            #     author.save()

        # local author - get from db
        else:
            try:
                author  = Author.objects.get(id=author_id1)
            except Author.DoesNotExist as e:
                return Response({"message":"Author does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        # list of uuid in string representation
        listOfPotentialFriendIds = data["authors"]
        listOfFriendIds = getAllFriends(author_id1)

        # convert list of uuid to strings
        for i in range(0, len(listOfFriendIds)):
            listOfFriendIds[i] = str(listOfFriendIds[i])
        resultList = list(set(listOfFriendIds) & set(listOfPotentialFriendIds))

        returnObj = { "query": "friends", "author": author_id1, "authors": resultList }
        return Response(returnObj, status=status.HTTP_200_OK)



class RequestList(generics.GenericAPIView):
    serializer_class = FriendingSerializer
    queryset = Friending.objects.all()

    def get(self, request, author_id1, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # return all auother_ids who author_id1 are following
        if author_id1 is not None:
            followerList = []
            aList = Friending.objects.filter(following__id=author_id1).values('author__id')
            for i in aList:
                followerList.append(i["author__id"])
        return Response({'query':'following', 'followers':followerList}, status=status.HTTP_200_OK)

class FriendRequest(generics.GenericAPIView):
    serializer_class = FriendingSerializer
    queryset = Friending.objects.all()

    def post(self, request, format=None):
        # ensure user is authenticated
        if (not request.user.is_authenticated()):
            return Response({'message':'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        if data == None:
            return Response({"message": "no body given."}, status=status.HTTP_400_BAD_REQUEST)

        # # check if request is from remote node, if so handle it
        # remoteNode = getRemoteNode(request.user)
        # if remoteNode != None:
        #     author_serializer = getRemoteAuthorProfile(remoteNode.url, request)
        #     # get remoteAuthor's Author object in our database (has id, displayname, host only - no user) if we already have it
        #     # else, create a new author object w/o user
        #     # author_of_request = remoteAuthor here
        #     try:
        #         author_of_request = Author.objects.get(id=author_serializer.data["id"])
        #     except Author.DoesNotExist as e:
        #         author_of_request = Author.objects.create(id=author_serializer.data["id"], displayname=author_serializer.data["displayname"], host=remoteNode.url)
        #         author_of_request.save()

        # # local author - get from db
        # else:
        #     author_of_request  = Author.objects.get(user=request.user)


        try:
            author_req= request.data["author"]
            friend_req = request.data["friend"]
        except:
            return Response({"message":"missing inputs"}, status=status.HTTP_400_BAD_REQUEST)

        atLeastOneAuthorIsLocal = False
        bothLocalAuthors = False
        try:
            author = Author.objects.get(id=author_req["id"])
            # it's a local user
            if request.get_host() in author.host: # author.user != None: 
                atLeastOneAuthorIsLocal = True
            # else is remote author sending the request
        except Author.DoesNotExist as e:
            # not local author - create remote author w/o user
            author = Author.objects.create(id=author_req["id"], displayname=author_req["displayname"], host=author_req["host"])
            author.save()

        try:
            friend = Author.objects.get(id=friend_req["id"])
            # it's a local user
            if request.get_host() in friend.host: # friend.user != None:
                if atLeastOneAuthorIsLocal:
                    bothLocalAuthors = True
                atLeastOneAuthorIsLocal = True

            # if friend is remote user
            else:
                return Response({"message":"Friend is not an author on this node"}, status=status.HTTP_400_BAD_REQUEST)

        except Author.DoesNotExist as e:
            return Response({"message":"Friend is not an author on this node"}, status=status.HTTP_400_BAD_REQUEST)

        if not atLeastOneAuthorIsLocal and not bothLocalAuthors:  # both remote users - client error - shouldn't have to handle this
            return Response({"message": "both are remote authors."}, status=status.HTTP_400_BAD_REQUEST)


        # we don't handle local to remote here - done in javascript - shouldn't hit our api

        # else if both are local or remote to local

        # check if friendship already exists in db
        try:
            friendship = Friending.objects.get(author=author, friend=friend)
            return Response({"message":"Relationship between author & friend already exists."}, status=status.HTTP_200_OK)
        except Friending.DoesNotExist as e:    
            serializer = FriendingSerializer(data=data)
            if serializer.is_valid():
                serializer.validated_data["author"] = author
                serializer.validated_data["friend"] = friend
                serializer.save()
                noti = Notification.objects.create(notificatee=Author.objects.get(id=friend_req["id"]), follower=Author.objects.get(id=author_req["id"]))
                noti.save()        
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)