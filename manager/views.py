from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from api.models import Author, Node, Friending
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from manager.forms import AuthorForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from post.models import Notification


# Create your views here.
# def register(request):
#     return render(request, "registration/signup.html")

def register(request):
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        user_form = UserCreationForm(data=request.POST)
        author_form = AuthorForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and author_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # User account is inactive by default
            # Users can only login into their account after admin's approval
            user.is_active = False
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            author = author_form.save(commit=False)
            author.user = user
            author.host = "http://" + request.get_host() + "/"

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                author.picture = request.FILES['picture']

            # Now we save the Author model instance.
            author.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, author_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserCreationForm()
        author_form = AuthorForm()

    # Render the template depending on the context.
    return render(request,
                  'registration/signup.html',
                  {'user_form': user_form, 'author_form': author_form, 'registered': registered})


def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)



        # # # Redirect admin to admin page
        # try:
        #     author = Author.objects.get(user=user)
        # except Author.DoesNotExist as e:
        #     if user:
        #         return HttpResponseRedirect('/admin')
        #     else:
        #         return render(request, "registration/login.html", {'message': "Invalid username or password."})

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # If an super user who is not admin tries to login
            # Add him into Author class
            try:
                author = Author.objects.get(user=user)
            except Author.DoesNotExist:
                author = Author.objects.create(user=user)
                author.save()

            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                return render(request, "registration/login.html", {'message': "Your account has not been activated."})
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return render(request, "registration/login.html", {'message': "Invalid username or password."})

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'registration/login.html', {})

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')


def manager(request):
    if request.user.is_staff:
        loggedInAuthor = Author.objects.get(user=request.user)
        authors = Author.objects.filter(host="http://"+request.get_host()+'/')
        nodes = Node.objects.all()
        return render(request, 'manager/admin.html', {'authors': authors, 'loggedInAuthor': loggedInAuthor, 'nodes': nodes})# 

# display friend request notification 
def friendRequest(request, username):
    if request.user.is_authenticated():
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            return render(request, "404_page.html", {'message': "User does not exist."})

        author = Author.objects.get(user=request.user)
        notis = Notification.objects.filter(notificatee=author)

        # notification on if logged in author has new follower
        followList = []
        followRelationships = Friending.objects.filter(friend=author)
        for relationship in followRelationships:
            followList.append(relationship.friend)

        if len(followList) > author.previous_follower_num:
            author.noti = True
            author.previous_follower_num = len(followList)
        else:
            author.noti = False
        author.save()

        return render(request, "manager/friendRequest.html",
                      {'notis': notis, 'user_account': user, 'loggedInAuthor': author})
    else:
        return HttpResponseRedirect(reverse('accounts_login')) 

