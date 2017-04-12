from django.shortcuts import render

from rest_framework import viewsets, mixins

from allauth.account.forms import LoginForm

from .serializers import ChoicesSerializer


def home(request):
    if not request.user.is_authenticated():
        login_form = LoginForm()
    else:
        login_form = None

    return render(request, 'core/home.html', {'form': login_form})


class ChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ChoicesSerializer
