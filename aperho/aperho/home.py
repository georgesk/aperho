from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *

def index_admin(request):
    return render(request, "home_admin.html")

def index(request):
    if request.user.is_authenticated():
        return render(request, "home.html")
    else:
        return HttpResponseRedirect("/login/")

