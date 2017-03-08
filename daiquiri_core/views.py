from django.shortcuts import render

from allauth.account.forms import LoginForm


def home(request):
    if not request.user.is_authenticated():
        login_form = LoginForm()
    else:
        login_form = None

    return render(request, 'core/home.html', {'form': login_form})
