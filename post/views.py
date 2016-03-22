from django.shortcuts import render
from django.template import RequestContext
from django.utils import timezone
from api.models import Post, Author, Comment, Friending, Node
from .forms import PostForm, CommentForm
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from api.views import PostList, CommentList, PostDetail
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from itertools import chain
from api.serializers import *
from django.http import HttpResponse
import urllib2
import json
import base64
import urllib
import uuid
from django.http import HttpResponse

# Create your views here.
'''
Handles submitting the Post form - used when creating a new Post
'''


def _submitPostForm(request, post_pk=None):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            if post_pk != None:
                response = PostList.as_view()(request, post_pk)
            else:
                response = PostList.as_view()(request)  # makes post call to API
            return response


'''
Renders the Public Stream page
'''


def public_stream(request):
    if (request.user.is_authenticated()):
        if request.method == "POST":
            response = _submitPostForm(request)

            # Empty Form Submitted
            if response == None:
                # alert user form was empty
                pass
            else:
                # -- TODO : display post success or failure on mainStream.html -- #
                if response.status_code == 201:
                    return HttpResponseRedirect('/success')
                else:  # 400 error
                    # alert user of the error
                    pass

        posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
        form = PostForm()

        # If an super user who is not admin tries to login
        # Add him into Author class
        try:
            author = Author.objects.get(user=request.user)
        except Author.DoesNotExist:
            author = Author.objects.create(user=request.user)
            author.save()

        # author = Author.objects.get(user=request.user)
        followList = []
        followRelationships = Friending.objects.filter(author=author)
        for relationship in followRelationships:
            followList.append(relationship.friend)
            
        # notification on if logged in author has new follower
        followerList = []
        followerRelationships = Friending.objects.filter(friend=author)
        for relationship in followerRelationships:
            followerList.append(relationship.friend)
        if len(followerList) > author.previous_follower_num:
            author.noti = True
            author.previous_follower_num = len(followerList)
        else:
            author.noti = False
        author.save()

        return render(request, 'post/mainStream.html', {'posts': posts, 'form': form, 'loggedInAuthor': author, 'followList': followList })
    else:
        return HttpResponseRedirect(reverse('accounts_login'))


'''
Renders the explore Stream
'''
def explore(request, node_id=None):
    if (request.user.is_authenticated()):
        nodes = Node.objects.all()
        author = Author.objects.get(user=request.user)
        if node_id == None:
            return render(request, 'explore.html', {'loggedInAuthor': author, 'nodes': nodes, 'all':True})
        else:
            #checks what node it is on and returns the public posts from that node
            
            node = Node.objects.get(id=node_id)
            url = node.url + "api/posts/"
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            req = urllib2.Request(url)
            credentials = { "http://project-c404.rhcloud.com/" : "team4:team4team4",\
                        "http://disporia-cmput404.rhcloud.com/": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ"}
            # set credentials on request
            if node.url == "http://project-c404.rhcloud.com/":
                    creds = base64.b64encode(credentials[node.url])
                    req.add_header("Authorization", "Basic " + creds)
            elif node.url == "http://disporia-cmput404.rhcloud.com/":
                    creds = credentials[node.url]
                    req.add_header("Authorization", "JWT " + creds)
            try:
                x = opener.open(req)
                y = x.read()
                jsonResponse = json.loads(y)
                postSerializer = PostSerializer(jsonResponse["posts"], many=True)
                posts = postSerializer.data

                form = PostForm()
                return render(request, 'explore.html', {'node':node,'posts': posts, 'form': form, 'loggedInAuthor': author, 'nodes': nodes, 'all':False})
            except urllib2.HTTPError, e:
                return render(request, "404_page.html", {'message': "HTTP ERROR: "+str(e.code)+" "+e.reason, 'loggedInAuthor': author},status=404)
    else:
        return HttpResponseRedirect(reverse('accounts_login'))

'''
Renders the post clicked from the explore page
'''
def explore_post(request, node_id, post_id):
    if (request.user.is_authenticated()):
        author = Author.objects.get(user=request.user)
        node = Node.objects.get(id=node_id)
        if node_id == None:
            return render(request, 'postDetail.html', {'loggedInAuthor': author, 'nodes': nodes})
        else:
            #checks what node it is on and returns the public posts from that node
            try:
                node = Node.objects.get(id=node_id)
                url = node.url + "api/posts/" + post_id +"/comments/"
                # opener = urllib2.build_opener(urllib2.HTTPHandler)
                # req = urllib2.Request(url)
                credentials = { "http://project-c404.rhcloud.com/" : "team4:team4team4",\
                        "http://disporia-cmput404.rhcloud.com/": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ"}
                if node.url == "http://project-c404.rhcloud.com/":
                        creds = base64.b64encode(credentials[node.url])
                        headers = {"Authorization" : "Basic " + creds}
                elif node.url == "http://disporia-cmput404.rhcloud.com/":
                        creds = credentials[node.url]
                        headers = {"Authorization": "JWT " + creds}

                #create the comment to be sent
                if request.method == "POST":
                    # set credentials on request
                    if node.url == "http://project-c404.rhcloud.com/":
                            values = {
                                       "comment":"hello11",
                                       "contentType": "text/plain",
                                       "author":   {
                                           "id": uuid.uuid4(),
                                           "host": "project-c404.rhcloud.com/api",
                                           "displayName": "team4",
                                           "url": "project-c404.rhcloud.com/api/author/a9661f41-827a-4588-bfcb-61bcfcf316ba",
                                           "github": ""
                                        },
                                       "visibility":"PUBLIC"
                                    }
                    elif node.url == "http://disporia-cmput404.rhcloud.com/":
                            values = {}

                    r = requests.post(url, json=values, headers=headers)
                     #send the request
                    print r.json()
                    print r.status_code
                    
                postSerializer = PostSerializer(jsonResponse)
                post = postSerializer.data
                post = {}
                commentForm = CommentForm()
                return render(request, 'post/postDetail.html', {'post': post, 'commentForm': commentForm, 'loggedInAuthor': author, 'node': node})
            except urllib2.HTTPError, e:
                return render(request, "404_page.html", {'message': "HTTP ERROR: "+str(e.code)+" "+e.reason, 'loggedInAuthor': author},status=e.code)
    else:
        return HttpResponseRedirect(reverse('accounts_login'))

'''
Renders the My Stream page
'''
def my_stream(request):
    if (request.user.is_authenticated()):
        if request.method == "POST":
            response = _submitPostForm(request)

            # Empty Form Submitted
            if response == None:
                # alert user form was empty
                pass
            else:
                # -- TODO : display post success or failure on mainStream.html -- #
                if response.status_code == 201:
                    return HttpResponseRedirect('/success')
                else:  # 400 error
                    # alert user of the error
                    pass

        author = Author.objects.get(user=request.user)

        # posts1 = Post.objects.filter(author=author).order_by('-published')

        # pks = []

        # #add the posts by the people we are friends with into our myStream
        # friend_pairs = Friending.objects.filter(author=author)
        # for i in range(len(friend_pairs)):
        #     friend_posts = Post.objects.filter(author=friend_pairs[i].friend)
        #     for j in range(len(friend_posts)):
        #         if isAllowed(request.user, friend_posts[j].id):
        #             pks.append(friend_posts[j].id)

        # #sort the posts so that the most recent is at the top
        # posts2 = Post.objects.filter(id__in=pks)
        # posts = posts1 | posts2
        # posts.order_by('-published')

        #bring in posts from node4A
        url = "http://cmput404team4b.herokuapp.com/api/posts"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        encodedValue = base64.b64encode("ab432861-f7bc-4b5b-9261-86c167615d6@nodeTeam4A:nodeTeam4A")
        req.add_header("Authorization", "Basic " + encodedValue)
        x = opener.open(req)
        y = x.read()
        jsonResponse = json.loads(y)
        postSerializer = PostSerializer(jsonResponse["posts"], many=True)
        posts = postSerializer.data

        followList = []
        # # notification on if logged in author has new follower
        # followList = []
        # followRelationships = Friending.objects.filter(friend=author)
        # for relationship in followRelationships:
        #     followList.append(relationship.friend)

        # if len(followList) > author.previous_follower_num:
        #     author.noti = True
        #     author.previous_follower_num = len(followList)
        # else:
        #     author.noti = False
        # author.save()
        # posts1 = Post.objects.filter(author=author).order_by('-published')

        # pks = []

        # #add the posts by the people we are friends with into our myStream
        # friend_pairs = Friending.objects.filter(author=author)
        # for i in range(len(friend_pairs)):
        #     friend_posts = Post.objects.filter(author=friend_pairs[i].friend)
        #     for j in range(len(friend_posts)):
        #         if isAllowed(request.user, friend_posts[j].id):
        #             pks.append(friend_posts[j].id)

        # #sort the posts so that the most recent is at the top
        # posts2 = Post.objects.filter(id__in=pks)
        # posts = posts1 | posts2
        # posts.order_by('-published')

        # # notification on if logged in author has new follower
        # followList = []
        # followRelationships = Friending.objects.filter(friend=author)
        # for relationship in followRelationships:
        #     followList.append(relationship.friend)

        # if len(followList) > author.previous_follower_num:
        #     author.noti = True
        #     author.previous_follower_num = len(followList)
        # else:
        #     author.noti = False
        # author.save()

        form = PostForm()
        return render(request, 'post/myStream.html', {'posts': posts, 'form': form, 'loggedInAuthor': author, 'followList': followList})
    else:
        return HttpResponseRedirect(reverse('accounts_login'))


'''
Handles submitting the Comment form - used when creating a new Comment
'''


def _submitCommentForm(request, post_pk):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            response = CommentList.as_view()(request, post_pk)  # makes post call to API
            return response


'''
Renders the page for specific post (including the post's comments)
'''


def post_detail(request, post_pk):
    if (request.user.is_authenticated()):
        if (isAllowed(request.user,post_pk)):
            if request.method == "POST":
                response = _submitCommentForm(request, post_pk)

                # Empty Form Submitted
                if response == None:
                    # alert user form was empty
                    pass
                else:
                    # -- TODO : display post success or failure on postDetail.html -- #
                    if ((response.status_code == 201) or (response.status_code == 200)):
                        return HttpResponseRedirect(reverse('post_detail_success', kwargs={'post_pk': post_pk}))
                    else:  # 400 error
                        # alert user of the error
                        pass

            post = Post.objects.get(pk=post_pk)
            form = CommentForm()
            author = Author.objects.get(user=request.user)
            return render(request, 'post/postDetail.html', {'post': post, 'commentForm': form, 'loggedInAuthor': author})
        else:
            return HttpResponseForbidden("You are not allowed to access this page")
    else:
        return HttpResponseRedirect(reverse('accounts_login'))


def post_edit(request, post_pk):
    if (request.user.is_authenticated()):
        if request.method == "POST":
            response = _submitPostForm(request, post_pk)

            # Empty Form Submitted
            if response == None:
                # alert user form was empty
                pass
            else:
                # -- TODO : display post success or failure on postDetail.html -- #
                if ((response.status_code == 201) or (response.status_code == 200)):
                    return HttpResponseRedirect(reverse('post_detail_success', kwargs={'post_pk': post_pk}))
                else:  # 400 error
                    # alert user of the error
                    pass

        post = Post.objects.get(pk=post_pk)
        form = PostForm(instance=post)
        author = Author.objects.get(user=request.user)    
        return render(request, 'post/postDetail.html', {'post': post, 'form': form, 'loggedInAuthor': author})
    else:
        return HttpResponseRedirect(reverse('accounts_login'))


def user_profile(request, user_id):
    if request.user.is_authenticated():
        try:
            profile_owner = Author.objects.get(id=user_id)
        except Author.DoesNotExist as e:
            # return render(request, "user_profile.html", {'posts': None, 'form': None, 'user_account': None})
            return render(request, "404_page.html", {'message': "Author does not exist."},status=404)

        # Delegates create post form submission
        if request.method == "POST":
            response = _submitPostForm(request)

            # Empty Form Submitted
            if response == None:
                # alert user form was empty
                pass
            else:
                # -- TODO : display post success or failure on mainStream.html -- #
                if response.status_code == 201:
                    return HttpResponseRedirect(reverse('user_profile_success', kwargs={'user_id': user_id}))
                else:  # 400 error
                    # alert user of the error
                    pass

        # FILTER POSTS BY VISIBILITY TO LOGGED IN USER --- #
        logged_author = Author.objects.get(user=request.user)
        if logged_author.user.is_staff:
            posts = Post.objects.filter(author=profile_owner,).order_by('-published')
        else:
            posts = Post.objects.filter(author=profile_owner, visibility='PUBLIC').order_by('-published')
        form = PostForm()
        r1List = Friending.objects.filter(author=profile_owner).select_related()
        r2List = Friending.objects.filter(friend=profile_owner).select_related()
        aList = []
        bList = []
        for relationship in r1List:
            aList.append(relationship.friend)
        for relationship in r2List:
            bList.append(relationship.author)

        friends = list(set(aList) & set(bList))

        # show follow or unfollow button according to the relationship between
        # logged author and profile's owner
        followList = []
        followRelationships = Friending.objects.filter(author=logged_author)
        for relationship in followRelationships:
            followList.append(relationship.friend)

        # follower_list
        # display profile owner 's follower'
        followers = []
        followersRelationships = Friending.objects.filter(friend=profile_owner)
        for relationship in followersRelationships:
            followers.append(relationship.author)

        return render(request, "user_profile.html",
                      {'posts': posts, 'form': form, 'profile_owner': profile_owner, 'loggedInAuthor': logged_author, 'followList': followList, 'followers': followers, 'friends': friends})
        
        # user_account is profile's owner
        # author is the one who logged into the system 
    else:
        return HttpResponseRedirect(reverse('accounts_login'))

'''
checks if a user is allowed access to a file

'''
def isAllowed(user,pk):
    post = Post.objects.get(id=pk)
    privacy = post.visibility
    viewer = Author.objects.get(user=user)

    #if the post was created by the user allow access
    if viewer == post.author :
        return True
    #if it is a public post allow everypne access
    elif privacy == "PUBLIC":
        return True
    elif privacy == "SERVER_ONLY":
        if viewer.host == post.author.host:
            return True
        else:
            return False
    #checks if another post is being shared with you
    elif privacy == "OTHERAUTHOR":
        user = User.objects.get(username=post.other_author)
        other_author = Author.objects.get(user=user)
        if other_author.id == viewer.id:
            return True
        else:
            return False
    #check if the user is in the friend list
    elif privacy == "FRIENDS" or privacy == "FOAF":
        friend_pairs = Friending.objects.filter(author=post.author)
        friends = []
        for i in range(len(friend_pairs)):
            backwards = Friending.objects.filter(author=friend_pairs[i].friend,friend=post.author)
            if len(backwards) > 0:
                friends.append(friend_pairs[i].friend)
        if viewer in friends:
            return True
        #check if the user is in the FoaF list
        elif privacy == "FOAF":
            for i in range(len(friends)):
                fofriend_pairs = Friending.objects.filter(author=friends[i])
                fofriends = []
                for j in range(len(fofriend_pairs)):
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
