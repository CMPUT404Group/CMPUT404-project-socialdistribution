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
import requests
from django.http import HttpResponse
from django import forms
from django.contrib.auth import authenticate
from datetime import datetime
from time import time
from django.conf import settings

#global variables
credentials = { "http://project-c404.rhcloud.com/" : "team4:team4team4",\
    "http://disporia-cmput404.rhcloud.com/": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg3MDI5Mzl9.cGDfv2lhFLNqOON3P4tq-LvoSTtarC5gIa1rG-ST5CA",\
    "http://mighty-cliffs-82717.herokuapp.com/" : "Team4:team4" }

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
        followList = []
        followRelationships = Friending.objects.filter(author=author)
        for relationship in followRelationships:
            followList.append(str(relationship.friend.id))
        if node_id == None:
            return render(request, 'explore.html', {'loggedInAuthor': author, 'nodes': nodes, 'all':True, 'followList': followList})
        else:
            #checks what node it is on and returns the public posts from that node

            node = Node.objects.get(id=node_id)
            url = node.url + "api/posts/"
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            req = urllib2.Request(url)
            try:
                # set credentials on request
                if node.url == "http://project-c404.rhcloud.com/" or node.url == "http://mighty-cliffs-82717.herokuapp.com/":
                    creds = base64.b64encode(credentials[node.url])
                    req.add_header("Authorization", "Basic " + creds)
                    x = opener.open(req)
                    y = x.read()
                    jsonResponse = json.loads(y)
                    postSerializer = PostSerializer(jsonResponse["posts"], many=True)
                elif node.url == "http://disporia-cmput404.rhcloud.com/":
                    creds = credentials[node.url]
                    req.add_header("Authorization", "JWT " + creds)
                    x = opener.open(req)
                    y = x.read()
                    jsonResponse = json.loads(y)
                    postSerializer = PostSerializer(jsonResponse["results"], many=True)

                posts = postSerializer.data
                for p in posts:
                    # fix date formatting
                    p = formatDate(p)

                form = PostForm()
                return render(request, 'explore.html', {'node':node,'posts': posts, 'form': form, 'loggedInAuthor': author, 'nodes': nodes, 'all':False, 'followList': followList})
            except urllib2.HTTPError, e:
                return render(request, "404_page.html", {'message': "HTTP ERROR: "+str(e.code)+" "+e.reason, 'loggedInAuthor': author},status=404)
    else:
        return HttpResponseRedirect(reverse('accounts_login'))

'''
Finds the posts for an author_id
'''
def get_APIAuthorPosts(friend_id):
    local = get_local(friend_id)
    if local != None and len(local) > 0:
        return local
    team5 = get_team5(friend_id)
    if  team5 != None and len(team5) > 0:
        return team5
    team6 = get_team5(friend_id)
    if team6 != None and len(team6) > 0:
        return team6
    team7 = get_team5(friend_id)
    if team7 != None and len(team7) > 0:
        return team6
    else:
        return []

'''
Get all the posts for a local author
'''
def get_local(author_id):
    #checks what node it is on and returns the public posts from that node
    try:
        url = settings.LOCAL_URL + "author/"+str(author_id)+"/posts"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        # set credentials on request
        creds =  base64.b64encode("test:test")
        req.add_header("Authorization", "Basic " + creds)
        x = opener.open(req)
        y = x.read()
        jsonResponse = json.loads(y)
        postSerializer = PostSerializer(jsonResponse["posts"], many=True)
        return postSerializer.data
    except urllib2.HTTPError, e:
        print("Local Error: "+str(e.code))

'''
Get all posts for <author> from team5
'''
def get_team5(author_id):
    #checks what node it is on and returns the public posts from that node
    try:
        url = "http://disporia-cmput404.rhcloud.com/api/author/"+str(author_id)+"/posts/"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        # set credentials on request
        req.add_header("Authorization", "JWT " + credentials["http://disporia-cmput404.rhcloud.com/"])
        x = opener.open(req)
        y = x.read()
        jsonResponse = json.loads(y)
        postSerializer = PostSerializer(jsonResponse["results"], many=True)
        for p in postSerializer.data:
            # fix date formatting
            p = formatDate(p)
        return postSerializer.data
    except urllib2.HTTPError, e:
        print("team 5 Error: "+str(e.code))

'''
Get all posts for <author> from team6
'''
def get_team6(author_id):
    try:
        #checks what node it is on and returns the public posts from that node
        url = "http://project-c404.rhcloud.com/api/author/"+str(author_id)+"/posts/"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        # set credentials on request
        req.add_header("Authorization", "Basic " + base64.b64encode(credentials["http://project-c404.rhcloud.com/"]))
        x = opener.open(req)
        y = x.read()
        jsonResponse = json.loads(y)
        if len(jsonResponse) > 0:
            postSerializer = PostSerializer(jsonResponse["posts"], many=True)
            for p in postSerializer.data:
                # fix date formatting
                p = formatDate(p)
            return postSerializer.data
        else:
            return []
    except urllib2.HTTPError, e:
        print("team 6 Error: "+str(e.code))

'''
Get all posts for <author> from team6
'''
def get_team7(author_id):
    try:
        #checks what node it is on and returns the public posts from that node
        url = "http://mighty-cliffs-82717.herokuapp.com/api/author/"+str(author_id)+"/posts/"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        # set credentials on request
        req.add_header("Authorization", "Basic " + base64.b64encode(credentials["http://mighty-cliffs-82717.herokuapp.com/"]))
        x = opener.open(req)
        y = x.read()
        jsonResponse = json.loads(y)
        if len(jsonResponse) > 0:
            postSerializer = PostSerializer(jsonResponse["posts"], many=True)
            for p in postSerializer.data:
                # fix date formatting
                p = formatDate(p)
            return postSerializer.data
        else:
            return []
    except urllib2.HTTPError, e:
        print("team 7 Error: "+str(e.code))

'''
Get a single post from someone's API
'''
def get_APIPost(post_id, host, header):
    #checks what node it is on and returns the public posts from that node
    url = host+str(post_id)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(url)
    # set credentials on request
    req.add_header("Authorization", header)
    x = opener.open(req)
    y = x.read()
    jsonResponse = json.loads(y)
    if host == "http://mighty-cliffs-82717.herokuapp.com/api/posts/":
        jsonResponse = jsonResponse["post"]
    postSerializer = PostSerializer(jsonResponse)
    return formatDate(postSerializer.data)

'''
Get all the friends for a particular author
'''
def get_APIFriends(person_id):
    t6_url = "http://project-c404.rhcloud.com/"
    t6_h = "Basic " + base64.b64encode(credentials[t6_url])
    t5_url = "http://disporia-cmput404.rhcloud.com/"
    t5_h = "JWT "+credentials[t5_url]
    t7_url = "http://mighty-cliffs-82717.herokuapp.com/"
    t7_h = "Basic " + base64.b64encode(credentials[t7_url])
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    try:
        url = settings.LOCAL_URL + "friends/" + str(person_id)
        req = urllib2.Request(url)
        creds = base64.b64encode("test:test")
        req.add_header("Authorization", "Basic " + creds)
        x = opener.open(req)
        y = x.read()
        return json.loads(y)["authors"]
    except urllib2.HTTPError, e:
        print("Not a local Person. Error: "+str(e.code))
    try:
        url = t5_url+"api/friends/"+str(person_id)
        req = urllib2.Request(url)
        req.add_header("Authorization", t5_h)
        x = opener.open(req)
        y = x.read()
        return json.loads(y)["authors"]
    except urllib2.HTTPError, e:
        print("Not a team 5 Person. Error: "+str(e.code))
    try:
        url = t6_url+"api/friends/"+str(person_id)
        req = urllib2.Request(url)
        req.add_header("Authorization", t6_h)
        x = opener.open(req)
        y = x.read()
        return json.loads(y)["authors"]
    except urllib2.HTTPError, e:
        print("Not a team 6 Person. Error: "+str(e.code))
    try:
        url = t7_url+"api/friends/"+str(person_id)
        req = urllib2.Request(url)
        req.add_header("Authorization", t7_h)
        x = opener.open(req)
        y = x.read()
        return json.loads(y)["authors"]
    except urllib2.HTTPError, e:
        print("Not a team 7 Person. Error: "+str(e.code))

'''
Create Comment to send to remote host
'''
def send_comment(request, post_id, node_id=None):
    data = request.POST
    author = Author.objects.get(user=request.user)
    comment = {}
    comment["comment"] = data["comment"]
    comment["contentType"] = data["contentType"]
    comment["author"] = {}
    comment["author"]["id"] = str(author.id)
    comment["author"]["host"] = author.host
    comment["author"]["displayName"] = author.displayName
    comment["author"]["github"] = author.github
    comment["author"]["url"] = author.url
    comment["visibility"] = "PUBLIC"
    comment["author"]["url"] = settings.LOCAL_URL + "author/"+str(author.id)
    #send it to a remote host
    if node_id != None:
        node = Node.objects.get(id=node_id)
        if node.url == "http://project-c404.rhcloud.com/" or node.url == "http://mighty-cliffs-82717.herokuapp.com/":
            url = node.url + "api/posts/" + post_id +"/comments/"
            creds = base64.b64encode(credentials[node.url])
            headers = {"Authorization" : "Basic " + creds}
            comment["author"]["url"] = settings.LOCAL_URL + "author/"+str(author.id)
        elif node.url == "http://disporia-cmput404.rhcloud.com/":
            url = node.url + "api/posts/" + post_id +"/comments"
            creds = credentials[node.url]
            headers = {"Authorization": "JWT " + creds}
            comment["author"]["url"] = "team4_url"

    #send it to a local host
    else:
        url = settings.LOCAL_URL + "posts/" + post_id +"/comments/"
        creds = base64.b64encode("test:test")
        headers = {"Authorization" : "Basic " + creds}
        #comment["author"]["id"] = "46410191-43e4-4a41-bd61-c8bd08e366f2"
    r = requests.post(url, json=comment, headers=headers)

'''
Renders the post clicked from the explore page
'''
def explore_post(request, node_id, post_id):
    t6_url = "http://project-c404.rhcloud.com/"
    t6_h = "Basic " + base64.b64encode(credentials[t6_url])
    t5_url = "http://disporia-cmput404.rhcloud.com/"
    t5_h = "JWT "+credentials[t5_url]
    t7_url = "http://mighty-cliffs-82717.herokuapp.com/"
    t7_h = "Basic " + base64.b64encode(credentials[t7_url])
    if (request.user.is_authenticated()):
        author = Author.objects.get(user=request.user)
        node = Node.objects.get(id=node_id)
        if node_id == None:
            return render(request, 'postDetail.html', {'loggedInAuthor': author, 'nodes': nodes, "remote":True})
        else:
            #checks what node it is on and returns the public posts from that node
            try:
                if node.url == "http://project-c404.rhcloud.com/":
                    post = get_APIPost(post_id,t6_url+"api/posts/", t6_h)
                elif node.url == "http://disporia-cmput404.rhcloud.com/":
                    post = get_APIPost(post_id,t5_url+"api/posts/", t5_h)
                elif node.url == "http://mighty-cliffs-82717.herokuapp.com/":
                    post = get_APIPost(post_id,t7_url+"api/posts/", t7_h)

                #create and send the comment if its allowed
                if request.method == "POST":
                    if (isAllowed(author,post)):
                        send_comment(request, post_id, node_id)
                        if node.url == "http://project-c404.rhcloud.com/":
                            post = get_APIPost(post_id,t6_url+"api/posts/", t6_h)
                        elif node.url == "http://disporia-cmput404.rhcloud.com/":
                            post = get_APIPost(post_id, t5_url+"api/posts/", t5_h)
                        elif node.url == "http://mighty-cliffs-82717.herokuapp.com/":
                            post = get_APIPost(post_id, t7_url+"api/posts/", t7_h)
                    else:
                        return HttpResponseForbidden("You are not allowed to access this page")
                # fix date formatting
                # post = formatDate(post)

                #display the post if its allowed
                if (isAllowed(author,post)):
                    commentForm = CommentForm()
                    return render(request, 'post/postDetail.html', {'remote':True, 'post': post, 'commentForm': commentForm, 'loggedInAuthor': author, 'node': node})
                else:
                    return HttpResponseForbidden("You are not allowed to access this page")
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
                    return HttpResponseRedirect('/myStream')#stay on myStream after posting
                else:  # 400 error
                    # alert user of the error
                    pass

        author = Author.objects.get(user=request.user)

        ##################### notification on if logged in author has new follower
        followList = []
        followRelationships = Friending.objects.filter(friend=author)

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
        ################## end of notification block

        posts = []

        #get the ids of the people you are following
        friends = []
        followers =  Friending.objects.filter(author=author)
        for follower in followers:
            friends.append(str(follower.friend.id))
        #add the posts by the people we are friends with into our myStream
        viewer_id = author.id
        #viewer_id = "13c4bb0f-f324-427e-8722-0f90c57176c4" # Test it with this when not on the heroku account
        for i in range(len(friends)):
            posts_all = []
            friend = friends[i]
            #get all the posts for a friend
            posts_all = get_APIAuthorPosts(friend)
            for j in range(len(posts_all)):
                if isAllowed(author, posts_all[j]):
                    posts.append(posts_all[j])

        #get all posts by the logged in author
        try:
            mine = get_APIAuthorPosts(viewer_id)
            posts.extend(mine)
        except urllib2.HTTPError, e:
            print("Couldnt get own posts "+author.user.username+" "+str(e.code))

        #TODO order from newest to oldest
        form = PostForm()
        return render(request, 'post/myStream.html', {'posts': posts, 'form': form, 'loggedInAuthor': author, 'followList': followList})
    else:
        return HttpResponseRedirect(reverse('accounts_login'))

# '''
# Handles submitting the Comment form - used when creating a new Comment
# '''

# def _submitCommentForm(request, post_pk):
#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             response = CommentList.as_view()(request, post_pk)  # makes post call to API
#             return response

'''
Renders the page for specific post (including the post's comments)
'''
def post_detail(request, post_pk):
    t6_url = "http://project-c404.rhcloud.com/"
    t6_h = "Basic " + base64.b64encode(credentials[t6_url])
    t5_url = "http://disporia-cmput404.rhcloud.com/"
    t5_h = "JWT "+credentials[t5_url]
    t7_url = "http://mighty-cliffs-82717.herokuapp.com/"
    t7_h = "Basic " + base64.b64encode(credentials[t7_url])
    if (request.user.is_authenticated()):
        viewer = Author.objects.get(user=request.user)
        ####TEMPORARY Check what node the post came from
        Found = False
        local = True
        try:
            post = get_APIPost(post_pk,settings.LOCAL_URL + "posts/","Basic " + base64.b64encode("test:test"))
            Found = True
        except urllib2.HTTPError, e:
            print("Not a local Post. Error: "+str(e.code))
            local = False
        try:
            post = get_APIPost(post_pk,t5_url+"api/posts/", t5_h)
            node = "55e70a0a-a284-4ffb-b192-08d083f4f164"
            page = explore_post(request, node, post_pk)
            return page
        except urllib2.HTTPError, e:
            print("Not a team 5 Post. Error: "+str(e.code))
        try:
            post = get_APIPost(post_pk,t6_url+"api/posts/", t6_h)
            node = "1a3f4b77-a4b7-405e-9dd7-fcb40e925c61"
            page = explore_post(request, node, post_pk)
            return page
        except urllib2.HTTPError, e:
            print("Not a team 6 Post. Error: "+str(e.code))
        try:
            post = get_APIPost(post_pk,t7_url+"api/posts/", t7_h)
            node = "c1893d94-cbb4-4dfa-a137-85b4637b58dc"
            page = explore_post(request, node, post_pk)
            return page
        except urllib2.HTTPError, e:
            print("Not a team 7 Post. Error: "+str(e.code))
        #############################
        if Found == True:
            if local == False:
                # format date for remote posts
                post = formatDate(post)

            if (isAllowed(viewer,post)):
                if request.method == "POST":
                    #response = _submitCommentForm(request, post_pk)
                    response = send_comment(request, post_pk, None)
                post = get_APIPost(post_pk,settings.LOCAL_URL + "posts/","Basic "+base64.b64encode("test:test"))
                form = CommentForm()
                author = Author.objects.get(user=request.user)
                return render(request, 'post/postDetail.html', {'remote':True,'post': post, 'commentForm': form, 'loggedInAuthor': author})
            else:
                return HttpResponseForbidden("You are not allowed to access this page")
        else:
            return render(request, "404_page.html", {'message': "Post Not Found",'loggedInAuthor': viewer},status=404)
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
        #post = formatDate(post)
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
            if 'old_password' in request.POST:
                changed = postChangeUserPassword(request, profile_owner)
                if not changed:
                    return HttpResponseRedirect(reverse('user_profile_success', kwargs={'user_id': user_id}), status = 400)

            else:
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
def isAllowed(viewer,post):
    viewer_id = viewer.id
    #viewer_id = "13c4bb0f-f324-427e-8722-0f90c57176c4"
    privacy = post["visibility"]
    #if the post was created by the user allow access
    if viewer_id == post["author"]["id"]:
        return True
    #if it is a public post allow everypne access
    elif privacy == "PUBLIC":
        return True
    elif privacy == "SERVER_ONLY":
        if viewer.host == post["author"]["host"]:
            return True
        else:
            return False
    #checks if another post is being shared with you -> not too great
    elif privacy == "OTHERAUTHOR":
        other_username = post["other_author"]
        if other_username == viewer.user.username:
            return True
        else:
            return False
    #check if the user is in the friend list - TODO
    elif privacy == "FRIENDS" or privacy == "FOAF":
        #get the author's friends
        friend_id = post["author"]["id"]
        friends = get_APIFriends(friend_id)
        if viewer_id in friends:
            return True
        elif privacy == "FOAF":
            #check the friend of friends
            for i in range(len(friends)):
                fofriends = get_APIFriends(friends[i])
                if viewer_id in fofriends:
                    return True
            return False
        else:
            return False
    else:
        return False

# adapted from: http://stackoverflow.com/questions/16700968/check-existing-password-and-reset-password
def postChangeUserPassword(request, profile_owner):
    old_password = str(request.POST['old_password'].strip())
    reset_password = str(request.POST['reset_password'].strip())
    new_password = str(request.POST['new_password'].strip())

    if (old_password and reset_password and reset_password == new_password):
        saveuser = User.objects.get(id=profile_owner.user.id)

        if saveuser.check_password(old_password):
            saveuser.set_password(request.POST['reset_password']);
            saveuser.save()
            return True

    return False

# fix date formatting
def formatDate(post):
    date = datetime.strptime(post['published'][0:10], "%Y-%m-%d")
    time = datetime.strptime(post['published'][11:16], "%H:%M")
    date_time = datetime.combine(date, datetime.time(time))
    post['published'] = date_time.strftime("%b %d, %Y, %-I:%M %p")
    return post
