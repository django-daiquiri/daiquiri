from django.shortcuts import render


def home(request):
    login_form = False

    return render(request, 'core/home.html', {'login_form': login_form})
