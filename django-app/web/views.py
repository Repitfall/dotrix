from django.shortcuts import render


def index(request):
    """Главная страница"""
    return render(request, "index.html")


def user_login(request):
    """Страница авторизации"""
    return render(request, "login.html")
