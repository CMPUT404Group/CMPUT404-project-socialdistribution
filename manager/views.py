from django.shortcuts import render
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect

# Create your views here.
# --- DOESN"T WORK YET --- #
def signup(request):
	return render(request, "registration/signup.html")