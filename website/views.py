from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import requests
from .forms import LoginForm
from .models import Transaction


def index(request):
    return render(request, 'website/index.html', context=None)

def login_user(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            recaptchaResponse = request.POST.get('g-recaptcha-response')
            # print(reca)
            url = 'https://www.google.com/recaptcha/api/siteverify'
            data = {
                'secret' : '6LcqCWwUAAAAAC9-4iofBAthF8pwPHQlSg6n9w4O',
                'response' : recaptchaResponse
            }
            r = requests.post(url, data=data)
            result = r.json()
            if result['success']:
                username = request.POST.get('username')
                password = request.POST.get('password')

                user = authenticate(request, username=username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect('home')
                return render(request, 'website/login.html')
            else:
                return render(request, 'website/login.html')


            
        return render(request, 'website/login.html', context=None)
    else:
        return render(request, 'website/index.html', context=None)

def register_user(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            address = request.POST.get('address')
            # username = request.POST.get('username')  already there
            phoneNum = request.POST.get('phoneNum')
            plaintextPassword = request.POST.get('password') #change to MD5

    else:
        return render(request, 'website/index.html', context=None)


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'website/index.html', context=None)

def transact(request):
    # form = #transaction form
    # if request.method == 'POST':
    #     if form.is_valid():
    #         amount = form.cleaned_data['amount']
    #         ifsccode = form.cleaned_data['ifsccode']
    #         accNum = form.cleaned_data['accNum']
    #         bankName = form.cleaned_data['bankName']
    #         # recepientAccount = form.cleaned_data['receiver'] # we won't get the account object directly. We will only get the details
    #         if float(amount) > 100000:
    #             isCritical = True
    #         else:
    #             isCritical = False
    #         transaction = Transaction.create(amount, request.user, recepientAccount, isCritical)
    return render(request, 'website/transact.html')

def debitMoney(request):
    # form = debitMoney
    if request.method == 'POST':
        if form.is_valid():
            amount = form.cleaned_data['amount']
                                

def creditMoney(request):
    # form = creditMoney
    if request.method == 'POST':
        if form.is_valid():
            amount = form.cleaned_data['amount']
            transaction = Transaction.create(amount, request.user, )                                    