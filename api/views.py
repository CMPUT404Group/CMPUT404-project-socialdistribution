from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from api.models import Post, Comment, Image, Friending, Author
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
    elif privacy == Post.OTHERAUTHOR:
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
            responseStatus = status.HTTP_201_CREATED
            if post_pk != None:
                post = get_object_or_404(Post, pk=post_pk)
                # only allow author of the post to modify it
                author = Author.objects.get(user=request.user)
                if author == post.author:
                    serializer = PostSerializer(post, data=request.data)
                    responseStatus=status.HTTP_200_OK
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
                return Response(serializer.data, status=responseStatus)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



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

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            author_id = Author.objects.get(user=request.user).id
            try:
                if (isAllowed(pk, author_id)):
                    post = self.get_object(pk)
                    serializer = PostSerializer(post)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            except Post.DoesNotExist as e:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):

            try:
                post = self.get_object(pk)
            except Post.DoesNotExist as e:
                return Response(status=status.HTTP_404_NOT_FOUND)

            # only allow author of the post to modify it
            if Author.objects.get(user=request.user) == post.author:
                serializer = PostSerializer(post, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # if logged in user is not author of the post
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            try:
                post = self.get_object(pk)
            except Post.DoesNotExist as e:
                return Response(status=status.HTTP_404_NOT_FOUND)

            # only allow author of the post to modify it
            if Author.objects.get(user=request.user)== post.author:
                post.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            # if logged in user is not author of the post
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



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
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            # --- TODO : Only authorize users to read/get this post if visibility/privacy settings allow it
            author_id = Author.objects.get(user=request.user).id
            if(isAllowed(post_pk, author_id)):
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

            author_id = Author.objects.get(user=request.user).id
            if(isAllowed(post_pk, author_id)):
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

    def get_object(self, pk):
        return get_object_or_404(Comment, pk=pk)

    def get(self, request, post_pk, comment_pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):

            # --- TODO : Only authorize users to read/get this comment if visibility/privacy settings of the corresponding post allow it
            author_id = Author.objects.get(user=request.user).id
            if(isAllowed(post_pk, author_id)):
                comment = self.get_object(comment_pk)
                serializer = CommentSerializer(comment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    # need to fix
    def put(self, request, post_pk, comment_pk, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
            comment = self.get_object(comment_pk)

            # only allow author of the comment to modify it
            if Author.objects.get(user=request.user) == comment.author:
                post = Post.objects.get(id=post_pk)
                serializer = CommentSerializer(post, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
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
        if (request.user.is_authenticated()):
            images = Image.objects.order_by('-upload_date')
            page = self.paginate_queryset(images)
            if page is not None:
                serializer = ImageSerializer(page, many=True)
                return self.get_paginated_response({"data":serializer.data, "query": "images"})
            #else:

        else:
            return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)

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
        if (request.user.is_authenticated()):
            authors = Author.objects.all()
            serializer = AuthorSerializer(authors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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
                except DoesNotExist as e:
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
            aList = Friending.objects.filter(author=author)
            # friendsList = getAllFriends(author.id)
            for person_pair in aList:
                # backwards check
                if len(Friending.objects.filter(author=person_pair.friend, friend=author)) > 0:
                    friendsList.append(person_pair.friend)
            serializer = AuthorSerializer(friendsList, many=True)
            responseData["friends"] = serializer.data

            responseData["url"] = author.host + "author/" + author.user.username

            return Response(responseData, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, author_pk=None, format=None):
        if (request.user.is_authenticated()):

            # update profile picture only
            if (request.data["github_name"] == "" and 
                request.data['host'] == "" and request.data["picture"] != ""):
                author = get_object_or_404(Author, pk=author_pk)
                if request.user == author.user:
                    author.picture = request.data["picture"]
                    author.save()
                    serializer = AuthorSerializer(author)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                   return Response(status=status.HTTP_403_FORBIDDEN)



            # NOT WORKING YET STILL DREADED KEYERROR


            else:   
                if author_pk != None:
                    author = get_object_or_404(Author, pk=author_pk)
                    # only allow author of the post to modify it
                    if request.user == author.user:
                        try:
                            author.github_name = request.data["github_name"]
                            author.save()
                            serializer = AuthorSerializer(author)
                        except KeyError:
                            print("what tyhe fuck?")
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
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


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
        if request.user.is_authenticated():

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
                friendsList = getAllFriends(author_id1)
                return Response({'query':'friends', 'authors': friendsList}, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



class RequestList(generics.GenericAPIView):
    serializer_class = FriendingSerializer
    queryset = Friending.objects.all()

    def get(self, request, author_id1, format=None):
        # ensure user is authenticated
        if (request.user.is_authenticated()):
        # return all auother_ids who author_id1 are following
            if author_id1 is not None:
                followerList = []
                aList = Friending.objects.filter(following__id=author_id1).values('author__id')
                for i in aList:
                    followerList.append(i["author__id"])
            return Response({'query':'following', 'followers':followerList}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class FriendRequest(generics.GenericAPIView):
    serializer_class = FriendingSerializer
    queryset = Friending.objects.all()

    def post(self, request, format=None):
    # if (request.user.is_authenticated()):
        if request.data is not None:
            authorid = request.data["author"]["id"]
            friendid = request.data["friend"]["id"] 
        
#       author1 = Author.objects.get(id=authorid)
#       follow1 = Author.objects.get(id=friendid)
#       try:
#           Author.objects.get(id=author1)
#           Author.objects.get(id=friend1)
#       except:
#           return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = FriendingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data["author"] = Author.objects.get(id=authorid)
            serializer.validated_data["friend"] = Author.objects.get(id=friendid)
            serializer.save()
            noti = Notification.objects.create(notificatee=Author.objects.get(id=friendid), follower=Author.objects.get(id=authorid))
            noti.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    # else:
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

