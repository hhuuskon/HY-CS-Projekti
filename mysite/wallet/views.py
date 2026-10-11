import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render

logger = logging.getLogger('wallet')


@login_required
def index(request):
    return HttpResponse("Hello, %s. You're at the wallet index." % request.user.username)


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username taken')
            return render(request, 'wallet/register.html')

        # FLAW 4: the page tells the user how a good password looks like but it is never checked
        # FIX:
        # try:
        #     validate_password(password)
        # except ValidationError as e:
        #     for msg in e.messages:
        #         messages.error(request, msg)
        #     return render(request, 'wallet/register.html')

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('wallet:index')
    return render(request, 'wallet/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        user = authenticate(request, username=username, password=request.POST['password'])
        if user is None:
            # FLAW 5: log doesn't tell anything useful
            logger.error('error occurred')
            # FIX:
            # logger.warning('failed login, username: %s, ip: %s', username, request.META.get('REMOTE_ADDR'))
            messages.error(request, 'Wrong username or password')
            return render(request, 'wallet/login.html')
        login(request, user)
        # FIX: log successful logins too
        # logger.info('login, username: %s, ip: %s', username, request.META.get('REMOTE_ADDR'))
        return redirect('wallet:index')
    return render(request, 'wallet/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('wallet:login')
