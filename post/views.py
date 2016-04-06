from django.shortcuts import render
from django.template import RequestContext
from django.utils import timezone
from api.models import Post, Author, Comment, Friending, Node
from .forms import PostForm, CommentForm
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from itertools import chain
from api.serializers import *
import urllib2
import json
import base64
import urllib
import requests
from django import forms
from django.contrib.auth import authenticate
from datetime import datetime
from time import time
from django.conf import settings
from api.views import PostList, CommentList, PostDetail

#global variables
credentials = { "http://project-c404.rhcloud.com/" : "team4:team4team4",\
    "http://disporia-cmput404.rhcloud.com/": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlYW00IiwidXNlcl9pZCI6MiwiZW1haWwiOiIiLCJleHAiOjE0NTg3MDI5Mzl9.cGDfv2lhFLNqOON3P4tq-LvoSTtarC5gIa1rG-ST5CA",\
    "http://mighty-cliffs-82717.herokuapp.com/" : "Team4:team4",\
    "http://secret-inlet-51780.herokuapp.com/":"team4:team4team4"}

FLAG_FRIENDS = 1

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
                if response.status_code == 201:
                    return HttpResponseRedirect('/success')
                else:
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
                if node.url == "http://project-c404.rhcloud.com/" or node.url == "http://mighty-cliffs-82717.herokuapp.com/" or node.url == "http://secret-inlet-51780.herokuapp.com/":
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
                return render(request, "404_page.html", {'message': "HTTP ERROR: "+str(e.code)+" "+e.reason, 'loggedInAuthor': author},status=e.code)
    else:
        return HttpResponseRedirect(reverse('accounts_login'))

'''
Finds the posts for an author_id
'''
def get_APIAuthorPosts(friend_id):
    friend = Author.objects.get(id=friend_id)

    if friend.host == settings.LOCAL_URL[:-4]:
        print "LOCAL TEAM"
        serializer = PostSerializer(Post.objects.filter(author=friend), many=True)
        # return serializer.data
        posts = serializer.data

    elif friend.host == "https://mighty-cliffs-82717.herokuapp.com/":
        print "Team 7"
        posts =  get_team7(friend_id)

    elif (friend.host == "project-c404.rhcloud.com/api") or (friend.host == "project-c404.rhcloud.com/api/"):
        print "Team 6"
        posts = get_team6(friend_id)

    elif friend.host == "secret-inlet-51780.herokuapp.com":
        print "Team 8"
        posts = get_team8(friend_id)

    else:
        print "No matching hosts. " + str(friend_id) + " | " + str(friend.host)
        posts = []

    for p in posts:
        try:
            # fix date formatting
            p = formatDate(p)
        except:
            continue

    return posts

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
        return postSerializer.data
    except urllib2.HTTPError, e:
        print("team 5 Error: "+str(e.code))
    # return []

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
            return postSerializer.data
        else:
            return []
    except urllib2.HTTPError, e:
        print("team 6 Error: "+str(e.code))

'''
Get all posts for <author> from team7
'''
def get_team7(author_id):
    # return []
    try:
        # checks what node it is on and returns the public posts from that node
        url = "http://mighty-cliffs-82717.herokuapp.com/api/author/"+str(author_id)+"/posts/?id=" + str(author_id)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        # set credentials on request
        req.add_header("Authorization", "Basic " + base64.b64encode(credentials["http://mighty-cliffs-82717.herokuapp.com/"]))
        x = opener.open(req)
        y = x.read()
        jsonResponse = json.loads(y)
        if len(jsonResponse) > 0:
            postSerializer = PostSerializer(jsonResponse["posts"], many=True)
            return postSerializer.data
        else:
            return []
    except urllib2.HTTPError, e:
        print("team 7 Error: "+str(e.code))

'''
Get all posts for <author> from team8
'''
def get_team8(author_id):
    try:
        #checks what node it is on and returns the public posts from that node
        url = "http://secret-inlet-51780.herokuapp.com/api/author/"+str(author_id)+"/posts/"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        # set credentials on request
        req.add_header("Authorization", "Basic " + base64.b64encode(credentials["http://secret-inlet-51780.herokuapp.com/"]))
        x = opener.open(req)
        y = x.read()
        jsonResponse = json.loads(y)
        if len(jsonResponse) > 0:
            postSerializer = PostSerializer(jsonResponse["posts"], many=True)
            return postSerializer.data
        else:
            return []
    except urllib2.HTTPError, e:
        print("team 8 Error: "+str(e.code))

'''
Get a single post from someone's API
'''
def get_APIPost(post_id, host, header):
    print "**  IN GET APIPOST :"
    print host
    print post_id

    if host == settings.LOCAL_URL + "posts/":
        print "ZERO LOCAL"
        post = PostSerializer(Post.objects.get(id=post_id)).data
        print "ZERO POST DATA : ",
        returnValue = formatDate(post)
        print returnValue
        return returnValue




    #checks what node it is on and returns the public posts from that node
    url = host+str(post_id)
    print "URL : ",
    print url
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    print "one"
    req = urllib2.Request(url)
    print "two"
    print req
    # set credentials on request
    print "Header : ",
    print header
    req.add_header("Authorization", header)
    print "Request : ",
    print req
    x = opener.open(req)
    print "three"
    print x
    y = x.read()
    print "four"
    print y
    jsonResponse = json.loads(y)
    print "five"
    print jsonResponse
    if host == "http://mighty-cliffs-82717.herokuapp.com/api/posts/":
        jsonResponse = jsonResponse["post"]
    postSerializer = PostSerializer(jsonResponse)
    print "six"
    print postSerializer.data
    returnValue = formatDate(postSerializer.data)
    print "seven"
    print returnValue
    return returnValue

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
    t8_url = "http://secret-inlet-51780.herokuapp.com/"
    t8_h = "Basic " + base64.b64encode(credentials[t8_url])
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
    try:
        url = t8_url+"api/friends/"+str(person_id)
        req = urllib2.Request(url)
        req.add_header("Authorization", t8_h)
        x = opener.open(req)
        y = x.read()
        return json.loads(y)["authors"]
    except urllib2.HTTPError, e:
        print("Not a team 8 Person. Error: "+str(e.code))


'''
Get all the friends for a particular author
'''
def get_APIFriends_myStream(person_id, person_host):
    t6_url = "http://project-c404.rhcloud.com/"
    t6_h = "Basic " + base64.b64encode(credentials[t6_url])
    t5_url = "http://disporia-cmput404.rhcloud.com/"
    t5_h = "JWT "+credentials[t5_url]
    t7_url = "http://mighty-cliffs-82717.herokuapp.com/"
    t7_h = "Basic " + base64.b64encode(credentials[t7_url])
    t8_url = "http://secret-inlet-51780.herokuapp.com/"
    t8_h = "Basic " + base64.b64encode(credentials[t8_url])
    opener = urllib2.build_opener(urllib2.HTTPHandler)


    if person_host == settings.LOCAL_URL[:-4]:
        print "LOCAL TEAM"
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

    elif person_host == "https://mighty-cliffs-82717.herokuapp.com/":
        print "Team 7"
        try:
            url = t7_url+"api/friends/"+str(person_id)
            req = urllib2.Request(url)
            req.add_header("Authorization", t7_h)
            x = opener.open(req)
            y = x.read()
            return json.loads(y)["authors"]
        except urllib2.HTTPError, e:
            print("Not a team 7 Person. Error: "+str(e.code))

    elif person_host == "project-c404.rhcloud.com/api":
        print "Team 6"
        try:
            url = t6_url+"api/friends/"+str(person_id)
            req = urllib2.Request(url)
            req.add_header("Authorization", t6_h)
            x = opener.open(req)
            y = x.read()
            return json.loads(y)["authors"]
        except urllib2.HTTPError, e:
            print("Not a team 6 Person. Error: "+str(e.code))

    elif person_host == "secret-inlet-51780.herokuapp.com":
        print "Team 8"
        try:
            url = t8_url+"api/friends/"+str(person_id)
            req = urllib2.Request(url)
            req.add_header("Authorization", t8_h)
            x = opener.open(req)
            y = x.read()
            return json.loads(y)["authors"]
        except urllib2.HTTPError, e:
            print("Not a team 8 Person. Error: "+str(e.code))

    elif person_host == "http://disporia-cmput404.rhcloud.com/":
        print "Team 5"
        try:
            url = t5_url+"api/friends/"+str(person_id)
            req = urllib2.Request(url)
            req.add_header("Authorization", t5_h)
            x = opener.open(req)
            y = x.read()
            return json.loads(y)["authors"]
        except urllib2.HTTPError, e:
            print("Not a team 5 Person. Error: "+str(e.code))

    else:
        print "No matching hosts - get_APIFriends - mystream"
        return []


'''
Create Comment to send to remote host
'''
def send_comment(request, post_id, node_id=None):
    print "IN SEND COMMENT"

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
    print "C1"
    #send it to a remote host
    if node_id != None:
        node = Node.objects.get(id=node_id)
        if node.url == "http://project-c404.rhcloud.com/" or node.url == "http://mighty-cliffs-82717.herokuapp.com/" or node.url =="http://secret-inlet-51780.herokuapp.com/":
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
        print "C2"
        url = settings.LOCAL_URL + "posts/" + post_id +"/comments/"
        creds = base64.b64encode("test:test")
        headers = {"Authorization" : "Basic " + creds}
        print "C3"

    print "C4"
    print comment
    print headers
    print url
    r = requests.post(url, json=comment, headers=headers)
    print r

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
    t8_url = "http://secret-inlet-51780.herokuapp.com/"
    t8_h = "Basic " + base64.b64encode(credentials[t8_url])
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
                elif node.url == "http://secret-inlet-51780.herokuapp.com/":
                    post = get_APIPost(post_id,t8_url+"api/posts/", t8_h)

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
                        elif node.url == "http://secret-inlet-51780.herokuapp.com/":
                            post = get_APIPost(post_id, t8_url+"api/posts/", t8_h)
                    else:
                        return HttpResponseForbidden("You are not allowed to access this page")

                #display the post if its allowed
                if (isAllowed(author,post)):
                    commentForm = CommentForm()
                    comments = []
                    # displays the date nicely
                    for comment in post["comments"]:
                        try:
                            comment1 = formatDate(comment)
                            comments.append(comment1)
                        except:
                            comments.append(comment)
                    post["comments"] = comments
                    return render(request, 'post/postDetail.html', {'remote':True, 'post': post, 'commentForm': commentForm, 'loggedInAuthor': author, 'node': node})
                else:
                    return HttpResponseForbidden("You are not allowed to access this page")
            except urllib2.HTTPError, e:
                return render(request, "404_page.html", {'message': "HTTP ERROR: "+str(e.code)+" "+e.reason, 'loggedInAuthor': author},status=e.code)
    else:
        return HttpResponseRedirect(reverse('accounts_login'))


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
                if response.status_code == 201:
                    return HttpResponseRedirect('/myStream')#stay on myStream after posting
                else:
                    pass

        author = Author.objects.get(user=request.user)

        # #get the ids of the people you are following
        followList = []
        followRelationships = Friending.objects.filter(author=author)
        for relationship in followRelationships:
            followList.append(str(relationship.friend.id))

        ##################### notification on if logged in author has new follower
        followerList = []
        followerRelationships = Friending.objects.filter(friend=author)
        for relationship in followerRelationships:followerList.append(relationship.friend)

        if len(followerList) > author.previous_follower_num:
            author.noti = True
            author.previous_follower_num = len(followerList)
        else:
            author.noti = False
        author.save()
        ################## end of notification block
        #
        posts = []
        # #add the posts by the people we are friends with into our myStream
        viewer_id = author.id

        friends = getAllFriends(viewer_id)
        for friend_id in friends:
            posts_all = get_APIAuthorPosts(friend_id)

            for post in posts_all:
                if isAllowed_myStream(author, post, FLAG_FRIENDS):
                    posts.append(post)


        following = [ rel.friend.id for rel in Friending.objects.filter(author=author)]

        followButNotFriends = list(set(following) - set(friends))

        for person_id in followButNotFriends:
            posts_all = get_APIAuthorPosts(person_id)

            for post in posts_all:
                if isAllowed_myStream(author, post):
                    posts.append(post)

        minePosts = get_APIAuthorPosts(viewer_id)
        for post in minePosts:
            posts.append(post)

        #orders from newest to oldest
        form = PostForm()

        # not working again - sorry
        # posts = sort_posts(posts)

        return render(request, 'post/myStream.html', {'posts': posts, 'form': form, 'loggedInAuthor': author, 'followList': followList})
    else:
        return HttpResponseRedirect(reverse('accounts_login'))


#sort the mystream posts by their published date
def sort_posts(posts):
    sorted_posts = []
    all_dates = []
    all_dates2 = []
    oldest = datetime.now()
    index = None

    for post in posts:
        date_time = datetime.strptime(post["published"],"%b %d, %Y, %I:%M %p")
        all_dates.append(date_time)
        all_dates2.append(date_time)

    all_dates.sort()
    for date in all_dates:
        i = all_dates2.index(date)
        sorted_posts.append(posts[i])

    return reversed(sorted_posts)
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
    t8_url = "http://secret-inlet-51780.herokuapp.com/"
    t8_h = "Basic " + base64.b64encode(credentials[t8_url])
    if (request.user.is_authenticated()):
        viewer = Author.objects.get(user=request.user)

        ####TEMPORARY Check what node the post came from
        Found = False
        local = True
        try:
            post = get_APIPost(post_pk,settings.LOCAL_URL + "posts/","Basic " + base64.b64encode("test:test"))
            print "1 : ",
            print post
            # post = PostSerializer(Post.objects.get(id=post_pk)).data
            # print "2 : ",
            # print post
            Found = True
            comments = []
            # displays the date nicely
            for comment in post["comments"]:
                comment1 = formatDate(comment)
                comments.append(comment1)
            post["comments"] = comments
            print
            print "3 : ",
            print post
            if Found == True:
                if local == False:
                    # format date for remote posts
                    post = formatDate(post)

                # if (isAllowed(viewer,post)):
                if request.method == "POST":
                    print "4 : send_comment call"
                    response = send_comment(request, post_pk, None)
                form = CommentForm()
                author = Author.objects.get(user=request.user)
                return render(request, 'post/postDetail.html', {'remote':True,'post': post, 'commentForm': form, 'loggedInAuthor': author})
                # else:
                    # return HttpResponseForbidden("You are not allowed to access this page")
            else:
                return render(request, "404_page.html", {'message': "Post Not Found",'loggedInAuthor': viewer},status=404)

        except urllib2.HTTPError, e:
            print("Not a local Post. Error: "+str(e.code))
            local = False
        except Post.DoesNotExist as e:
            print("Post is not local. Error: " + str(e))
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
            node = "469995bf-0d2f-4bc9-a7f3-49f6a58d13da"
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
        try:
            post = get_APIPost(post_pk,t8_url+"api/posts/", t8_h)
            node = "1636c703-aa1c-4f78-bdcf-fcf0dec56f16"
            page = explore_post(request, node, post_pk)
            return page
        except urllib2.HTTPError, e:
            print("Not a team 8 Post. Error: "+str(e.code))
        #############################

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
                if ((response.status_code == 201) or (response.status_code == 200)):
                    return HttpResponseRedirect(reverse('post_detail_success', kwargs={'post_pk': post_pk}))
                else:
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
                    if response.status_code == 201:
                        return HttpResponseRedirect(reverse('user_profile_success', kwargs={'user_id': user_id}))
                    else:
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
    #viewer_id = "4fd7e786-7307-47e0-80d4-2c7a5cd14cb4"
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
        friends = [ str(id) for id in get_APIFriends(friend_id) ]
        if str(viewer_id) in friends:
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


'''
checks if a user is allowed access to a file - used for mystream
'''
def isAllowed_myStream(viewer,post, flag=None):
    viewer_id = viewer.id
    #viewer_id = "4fd7e786-7307-47e0-80d4-2c7a5cd14cb4"
    privacy = post["visibility"]
    #if the post was created by the user allow access
    if str(viewer_id) == post["author"]["id"]:
        return True
    #if it is a public post allow everypne access
    elif privacy == Post.PUBLIC:
        return True
    elif privacy == Post.SERVER_ONLY:
        if viewer.host == post["author"]["host"]:
            return True
        else:
            return False
    #checks if another post is being shared with you -> not too great
    elif privacy == Post.OTHER_AUTHOR:
        other_username = post["other_author"]
        if other_username == viewer.user.username:
            return True
        else:
            return False
    elif privacy == Post.FRIENDS:
        if flag == FLAG_FRIENDS:
            return True

    elif privacy == Post.FRIENDS_OF_FRIENDS:
        if flag == FLAG_FRIENDS:
            return True

        myFriends = [ str(id) for id in getAllFriends(viewer_id) ]
        postAuthorID = post["author"]["id"]
        postAuthorHost = post["author"]["host"]
        postAuthorFriends = [ str(id) for id in get_APIFriends_myStream(postAuthorID, postAuthorHost) ]

        commonFriends = list(set(myFriends) & set(postAuthorFriends))

        if len(commonFriends) > 0:
            return True

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
    try:
        date = datetime.strptime(post['published'][0:10], "%Y-%m-%d")
        time = datetime.strptime(post['published'][11:16], "%H:%M")
        date_time = datetime.combine(date, datetime.time(time))
        post['published'] = date_time.strftime("%b %d, %Y, %-I:%M %p")
    except:
        return post
    return post
