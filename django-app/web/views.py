from django.shortcuts import render, redirect


def index(request):
    """Главная страница"""
    if request.user.is_authenticated:
        return render(request, "index.html")
    else:
        return redirect('login')


def user_login(request):
    """Страница авторизации"""
    return render(request, "login.html")
