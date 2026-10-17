import logging
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .keys import encrypt, decrypt, new_address, new_private_key
from .models import Wallet, Transaction

logger = logging.getLogger('wallet')


@login_required
def index(request):
    return redirect('wallet:detail', wallet_id=request.user.wallet.id)


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
        Wallet.objects.create(owner=user, address=new_address(), balance=100,
                              private_key=encrypt(new_private_key()))
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
            # logger.warning('failed login, username: %s', username)
            messages.error(request, 'Wrong username or password')
            return render(request, 'wallet/login.html')
        login(request, user)
        # FIX: log successful logins too
        # logger.info('login, username: %s', username)
        return redirect('wallet:index')
    return render(request, 'wallet/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('wallet:login')


@login_required
def detail(request, wallet_id):
    # FLAW 1: anyone logged in can open any wallet by changing the id in the url
    wallet = get_object_or_404(Wallet, pk=wallet_id)
    # FIX:
    # wallet = get_object_or_404(Wallet, pk=wallet_id, owner=request.user)
    transactions = Transaction.objects.filter(Q(sender=wallet) | Q(receiver=wallet)).order_by('-date')
    return render(request, 'wallet/detail.html', {
        'wallet': wallet,
        'private_key': decrypt(wallet.private_key),
        'transactions': transactions,
    })


@login_required
def send(request, wallet_id):
    # FLAW 1: same problem here, you can send money from other peoples wallets
    wallet = get_object_or_404(Wallet, pk=wallet_id)
    # FIX:
    # wallet = get_object_or_404(Wallet, pk=wallet_id, owner=request.user)
    if request.method != 'POST':
        return redirect('wallet:detail', wallet_id=wallet.id)
    try:
        amount = Decimal(request.POST['amount'])
        receiver = Wallet.objects.get(address=request.POST['address'].strip())
    except (InvalidOperation, Wallet.DoesNotExist):
        logger.error('error occurred')
        # FIX:
        # logger.warning('failed transfer, user: %s, wallet: %s', request.user.username, wallet.id)
        messages.error(request, 'Check amount and address')
        return redirect('wallet:detail', wallet_id=wallet.id)

    if amount <= 0 or amount > wallet.balance or receiver == wallet:
        logger.error('error occurred')
        messages.error(request, 'Not possible')
        return redirect('wallet:detail', wallet_id=wallet.id)

    wallet.balance -= amount
    receiver.balance += amount
    wallet.save()
    receiver.save()
    Transaction.objects.create(sender=wallet, receiver=receiver, amount=amount, note=request.POST.get('note', ''))
    # FIX:
    # logger.info('transfer, user: %s, from: %s, to: %s, amount: %s', request.user.username,
    #             wallet.address, receiver.address, amount)
    messages.success(request, 'Sent!')
    return redirect('wallet:detail', wallet_id=wallet.id)


@login_required
def search(request, wallet_id):
    wallet = get_object_or_404(Wallet, pk=wallet_id)
    # FIX (flaw 1):
    # wallet = get_object_or_404(Wallet, pk=wallet_id, owner=request.user)
    q = request.GET.get('q', '')

    # FLAW 3: sql injection, user input goes straight into the query
    sql = ("SELECT t.id, s.address, r.address, t.amount, t.note, t.date FROM wallet_transaction t "
           "JOIN wallet_wallet s ON t.sender_id = s.id JOIN wallet_wallet r ON t.receiver_id = r.id "
           "WHERE (t.sender_id = %s OR t.receiver_id = %s) AND t.note LIKE '%%%s%%'" % (wallet.id, wallet.id, q))
    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
    # FIX: use the orm (it uses parameters)
    # results = Transaction.objects.filter(Q(sender=wallet) | Q(receiver=wallet), note__contains=q) \
    #     .values_list('id', 'sender__address', 'receiver__address', 'amount', 'note', 'date')

    return render(request, 'wallet/search.html', {'wallet': wallet, 'q': q, 'results': results})
