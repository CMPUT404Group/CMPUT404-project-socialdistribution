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
            try:
                # set credentials on request
                if node.url == "http://project-c404.rhcloud.com/":
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

                form = PostForm()
                return render(request, 'explore.html', {'node':node,'posts': posts, 'form': form, 'loggedInAuthor': author, 'nodes': nodes, 'all':False})
            except urllib2.HTTPError, e:
                return render(request, "404_page.html", {'message': "HTTP ERROR: "+str(e.code)+" "+e.reason, 'loggedInAuthor': author},status=404)
    else:
        return HttpResponseRedirect(reverse('accounts_login'))

'''
Get all the posts for a local author
'''
def get_local(request, author_id):
    #checks what node it is on and returns the public posts from that node
    author = Author.objects.get(user=request.user)
    url = "http://cmput404-team-4b.herokuapp.com/api/author/4fd7e786-7307-47e0-80d4-2c7a5cd14cb4/posts"
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

'''
Get all posts for <author> from team5
'''
def get_team5(request, author_id):
    #checks what node it is on and returns the public posts from that node
    author = Author.objects.get(user=request.user)
    url = "http://disporia-cmput404.rhcloud.com/api/author/"+str(author_id)+"/posts/"
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(url)
    # set credentials on request
    creds =  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ"
    req.add_header("Authorization", "JWT " + creds) 
    x = opener.open(req)
    y = x.read()
    jsonResponse = json.loads(y)
    postSerializer = PostSerializer(jsonResponse["results"], many=True)
    return postSerializer.data

'''
Get all posts for <author> from team6
'''
def get_team6(request, author_id, node_id):
    #checks what node it is on and returns the public posts from that node
    author = Author.objects.get(user=request.user)
    node = Node.objects.get(id=node_id)
    url = "http://project-c404.rhcloud.com/api/author/"+str(author_id)+"/posts/"
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(url)
    # set credentials on request
    creds = base64.b64encode("team4:team4team4")
    req.add_header("Authorization", "Basic " + creds)
    x = opener.open(req)
    y = x.read()
    jsonResponse = json.loads(y)
    postSerializer = PostSerializer(jsonResponse["posts"], many=True)
    return postSerializer.data

'''
Get one post from team5 -> ("http://disporia-cmput404.rhcloud.com/api/posts/", "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ")
'''

'''
Get one post from team6 -> ("http://project-c404.rhcloud.com/api/posts/", "Basic " + base64.b64encode("team4:team4team4"))
'''

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
    postSerializer = PostSerializer(jsonResponse)
    return postSerializer.data
'''
Create Comment to send to remote host
'''
def send_comment(request, post_id, node_id=None):
    credentials = { "http://project-c404.rhcloud.com/" : "team4:team4team4",\
        "http://disporia-cmput404.rhcloud.com/": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg2MDQ5OTV9.yiiY5evZBCFhjUgCI0U5C76LrluI9eepyOqKUmLdcPE"}
    data = request.POST
    author = Author.objects.get(user=request.user)
    comment = {}
    comment["comment"] = data["comment"]
    comment["contentType"] = data["contentType"]
    comment["author"] = {}
    comment["author"]["id"] = str(author.id)
    comment["author"]["host"] = author.host
    comment["author"]["displayName"] = author.displayname
    comment["author"]["github"] = author.github
    comment["visibility"] = "PUBLIC"
    print(author.id)
    print(author.host)
    #send it to a remote host
    if node_id != None:
        node = Node.objects.get(id=node_id)
        if node.url == "http://project-c404.rhcloud.com/":
            url = node.url + "api/posts/" + post_id +"/comments/"
            creds = base64.b64encode(credentials[node.url])
            headers = {"Authorization" : "Basic " + creds}
            comment["author"]["url"] = "project-c404.rhcloud.com/api/author/a9661f41-827a-4588-bfcb-61bcfcf316ba"
        elif node.url == "http://disporia-cmput404.rhcloud.com/":
            url = node.url + "api/posts/" + post_id +"/comments"
            creds = credentials[node.url]
            headers = {"Authorization": "JWT " + creds}
            comment["author"]["url"] = "team4_url"
    #send it to a local host
    else:
        url = "http://cmput404-team-4b.herokuapp.com/api/posts/" + post_id +"/comments/"
        creds = base64.b64encode("test:test")
        headers = {"Authorization" : "Basic " + creds}
        #comment["author"]["id"] = "46410191-43e4-4a41-bd61-c8bd08e366f2"
    r = requests.post(url, json=comment, headers=headers)

'''
Renders the post clicked from the explore page
'''
def explore_post(request, node_id, post_id):
    if (request.user.is_authenticated()):
        author = Author.objects.get(user=request.user)
        node = Node.objects.get(id=node_id)
        if node_id == None:
            return render(request, 'postDetail.html', {'loggedInAuthor': author, 'nodes': nodes, "remote":True})
        else:
            #checks what node it is on and returns the public posts from that node
            try:
                #get the post
                if node.url == "http://project-c404.rhcloud.com/":
                    post = get_APIPost(post_id,"http://project-c404.rhcloud.com/api/posts/", "Basic " + base64.b64encode("team4:team4team4"))
                elif node.url == "http://disporia-cmput404.rhcloud.com/":
                    post = get_APIPost(post_id,"http://disporia-cmput404.rhcloud.com/api/posts/", "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ")

                #create and send the comment if its allowed
                if request.method == "POST":  
                    if (isAllowed(author,post)):                   
                        send_comment(request, post_id, node_id)
                        if node.url == "http://project-c404.rhcloud.com/":
                            post = get_APIPost(post_id,"http://project-c404.rhcloud.com/api/posts/", "Basic " + base64.b64encode("team4:team4team4"))
                        elif node.url == "http://disporia-cmput404.rhcloud.com/":
                            post = get_APIPost(post_id, "http://disporia-cmput404.rhcloud.com/api/posts/", "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ")
                    else:
                        return HttpResponseForbidden("You are not allowed to access this page")

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
                    return HttpResponseRedirect('/success')
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

        #add the posts by the people we are friends with into our myStream
        friend_pairs = Friending.objects.filter(author=author)
        for i in range(len(friend_pairs)):
            posts_all = []
            friend = friend_pairs[i].friend
            #these are from our local friends
            if request.META.get("HTTP_HOST") in friend.host:
                try:
                    posts_all = get_local(request, friend.id)
                except urllib2.HTTPError, e:
                    print("Couldnt get posts for local friend "+friend.user.username)
            #these are from our remote friends
            else:
                if friend.host == "project-c404.rhcloud.com/api":
                    node = "1a3f4b77-a4b7-405e-9dd7-fcb40e925c61"
                    try:
                        posts_all = get_team6(request, friend.id, node)
                    except urllib2.HTTPError, e:
                        print("Couldnt get posts for remote friend "+friend.user.username)
                elif friend.host == "" :
                    node = "55e70a0a-a284-4ffb-b192-08d083f4f164"
                    try:
                        posts_all = get_team5(request, friend.id, node)
                    except urllib2.HTTPError, e:
                        print("Couldnt get posts for remote friend "+friend.user.username)
                else:
                    pass
            for j in range(len(posts_all)):
                if isAllowed(author, posts_all[j]):
                    posts.append(posts_all[j])

        #get all posts by the logged in author
        try:      
            mine = get_local(request, author.id)
            posts.extend(mine)
        except urllib2.HTTPError, e:
            print("Couldnt get own posts "+author.user.username+str(e.code))

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
    if (request.user.is_authenticated()):
        viewer = Author.objects.get(user=request.user)
        ####TEMPORARY Check what node the post came from
        Found = False
        print(post_pk)
        try:
            post = get_APIPost(post_pk,"http://cmput404-team-4b.herokuapp.com/api/posts/","Basic "+base64.b64encode("test:test"))
            Found = True
        except urllib2.HTTPError, e:
            print("Not a local Post. Error: "+str(e.code))
        try:
            post = get_APIPost(post_pk,"http://disporia-cmput404.rhcloud.com/api/posts/", "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg1OTE1Nzd9.WjbgA_s-cWtNHzURwAceZOYuD4RASsSqqFiwnY58FqQ")
            node = "55e70a0a-a284-4ffb-b192-08d083f4f164"
            page = explore_post(request, node, post_pk)
            return page
        except urllib2.HTTPError, e:
            print("Not a team 5 Post. Error: "+str(e.code))
        try:
            post = get_APIPost(post_pk,"http://project-c404.rhcloud.com/api/posts/", "Basic " + base64.b64encode("team4:team4team4"))
            node = "1a3f4b77-a4b7-405e-9dd7-fcb40e925c61"
            page = explore_post(request, node, post_pk)
            return page
        except urllib2.HTTPError, e:
            print("Not a team 6 Post. Error: "+str(e.code))
        #############################
        if Found == True:
            if (isAllowed(viewer,post)):
                if request.method == "POST":
                    #response = _submitCommentForm(request, post_pk)
                    response = send_comment(request, post_pk, None)

                #post = Post.objects.get(pk=post_pk)
                post = get_APIPost(post_pk,"http://cmput404-team-4b.herokuapp.com/api/posts/","Basic "+base64.b64encode("test:test"))
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
            if 'reset_password' in request.POST:
                postChangeUserPassword(request, profile_owner)
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
    privacy = post["visibility"]

    #if the post was created by the user allow access
    if viewer.id == post["author"]["id"]:
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
    # elif privacy == "FRIENDS" or privacy == "FOAF":
    #     friend_pairs = Friending.objects.filter(author=post.author)
    #     friends = []
    #     for i in range(len(friend_pairs)):
    #         backwards = Friending.objects.filter(author=friend_pairs[i].friend,friend=post.author)
    #         if len(backwards) > 0:
    #             friends.append(friend_pairs[i].friend)
    #     if viewer in friends:
    #         return True
    #     #check if the user is in the FoaF list
    #     elif privacy == "FOAF":
    #         for i in range(len(friends)):
    #             fofriend_pairs = Friending.objects.filter(author=friends[i])
    #             fofriends = []
    #             for j in range(len(fofriend_pairs)):
    #                 backwards = Friending.objects.filter(friend=friends[i],author=fofriend_pairs[j].friend)
    #                 if len(backwards) > 0:
    #                     fofriends.append(fofriend_pairs[j].friend)
    #             if viewer in fofriends:
    #                 return True
        # #if not a friend return false
        # else:
        #     return False
    else:
        return False

# ref: http://stackoverflow.com/questions/16700968/check-existing-password-and-reset-password
# HASN'T BEEN QUITE TESTED OR IMPLEMENTED COMPLETELY YET
def postChangeUserPassword(request, profile_owner):
    old_password = str(request.POST['old_password'].strip())
    print(old_password)
    reset_password = str(request.POST['reset_password'].strip())
    new_password = str(request.POST['new_password'].strip())
       
    if (old_password and reset_password and reset_password == new_password):
        saveuser = User.objects.get(id=profile_owner.user.id)
        if saveuser.check_password(old_password):
            saveuser.set_password(request.POST['reset_password']);
            saveuser.save()
            #I DONT THINK WE NEED TO USE SERIALIZER or anything HERE???
            return True
    return False