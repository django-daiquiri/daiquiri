from django.shortcuts import render

from daiquiri_auth.forms import LoginForm


def home(request):
    login_form = LoginForm()

    return render(request, 'core/home.html', {'login_form': login_form})
