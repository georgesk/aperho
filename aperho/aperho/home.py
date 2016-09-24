from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *

def index_admin(request):
    return render(request, "home_admin.html")

def index(request):
    return render(request, "home.html")

def login(request):
    if request.method == 'POST':
        form = AuthenticationFormWithInactiveUsersOkay(request.POST or None)
        print("GRRR form.is_valid()", form.is_valid(), repr(form.errors))
        if form.is_valid():
            username_from_form = form.cleaned_data['username']
            password_from_form = form.cleaned_data['password']
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                print("GRRR", user)
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                return HttpResponse("Nom d'utilisateur ou mot de passe incorrects")
        else:
            #return HttpResponse(form.errors)
            return HttpResponse(request.POST)
    else:
        form = AuthenticationFormWithInactiveUsersOkay()
    return render(
        request,
        'login.html',
        {'form':form},
    )
