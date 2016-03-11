from django.shortcuts import render
from django.template import RequestContext
from django.utils import timezone
from api.models import Post, Author, Comment, Friending
from .forms import UploadFileForm, PostForm, CommentForm
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from api.views import PostList, CommentList, PostDetail
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

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
        author = Author.objects.get(user=request.user)
        return render(request, 'post/mainStream.html', {'posts': posts, 'form': form, 'loggedInAuthor': author})
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
        posts = Post.objects.filter(author=author).order_by('-published')
        form = PostForm()
        return render(request, 'post/mainStream.html', {'posts': posts, 'form': form, 'loggedInAuthor': author})
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
        if (isAllowed(request,post_pk)):
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
        return render(request, 'post/postDetail.html', {'post': post, 'form': form})
    else:
        return HttpResponseRedirect(reverse('accounts_login'))


def user_profile(request, username):
    if request.user.is_authenticated():
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            # return render(request, "user_profile.html", {'posts': None, 'form': None, 'user_account': None})
            return render(request, "404_page.html", {'message': "User does not exist."})

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
                    return HttpResponseRedirect(reverse('user_profile_success', kwargs={'username': username}))
                else:  # 400 error
                    # alert user of the error
                    pass

        # --- TODO : FILTER POSTS BY VISIBILITY TO LOGGED IN USER --- #
        author = Author.objects.get(user=request.user)
        posts = Post.objects.filter(author=author).order_by('-published')
        try:
            author = Author.objects.get(user=user)
        except Author.DoesNotExist as e:
            return render(request, "admin.html")

        form = PostForm()
        return render(request, "user_profile.html",
                      {'posts': posts, 'form': form, 'user_account': user, 'author': author})


    else:
        return HttpResponseRedirect(reverse('accounts_login'))


# for image uploads to save
def file(request):
    if request.method == "POST":
        img = UploadFileForm(request.POST, request.FILES)
        if img.is_valid():
            img.save()
            return HttpResponseRedirect(reverse('imageupload'))
    else:
        img = UploadFileForm()
    return render(request, 'file.html', {'form': img})


'''
checks if a user is allowed access to a file

'''
def isAllowed(request,pk):
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
        print(friend_pairs)
        for i in range(len(friend_pairs)):
            friends.append(friend_pairs[i].friend)
            print(friend_pairs[i].friend.user.username)
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