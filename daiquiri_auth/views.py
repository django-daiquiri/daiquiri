from django.shortcuts import render
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect

from .forms import LoginForm


def login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.login(request)
            if user:
                auth_login(request, user)
                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect('/')

    return render(request, 'auth/login.html', {'form': form})
