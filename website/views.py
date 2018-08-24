from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import requests
from .forms import LoginForm, RegisterForm
from .models import Transaction, Profile
from django.contrib.auth.models import User


def index(request):
    return render(request, 'website/index.html', context=None)

def login_user(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            login_form = LoginForm(request.POST)
            if login_form.is_valid():  
                recaptcha_response = request.POST.get('g-recaptcha-response')
                if recaptcha_response:
                    url = 'https://www.google.com/recaptcha/api/siteverify'
                    data = {
                        'secret' : '6LcqCWwUAAAAAC9-4iofBAthF8pwPHQlSg6n9w4O',
                        'response' : recaptcha_response
                    }
                    r = requests.post(url, data=data)
                    result = r.json()
                    if result['success']:
                        username = login_form.cleaned_data['username']
                        password = login_form.cleaned_data['password']

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
    form = RegisterForm
    if not request.user.is_authenticated:
        if request.method == "POST":
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                recaptcha_response = request.POST.get('g-recaptcha-response')
                if recaptcha_response:
                    url = 'https://www.google.com/recaptcha/api/siteverify'
                    data = {
                        'secret' : '6LcqCWwUAAAAAC9-4iofBAthF8pwPHQlSg6n9w4O',
                        'response' : recaptcha_response
                    }
                    r = requests.post(url, data=data)
                    result = r.json()
                    if result['success']:
                        user = register_form.save()
                        user.refresh_from_db()
                        
                        profile = Profile()
                        profile.user_id = user.id
                        profile.address = register_form.cleaned_data['address']
                        profile.phone_number = register_form.cleaned_data['contact']
                        profile.save()

                        user.email = register_form.cleaned_data['email_address']

                        user.set_password(register_form.cleaned_data['password'])
                        user.save()
                        login(request, user)
                        return redirect('home')
                    else:
                        return render(request, 'website/register.html', context={"form": form})
        return render(request, 'website/register.html', context={"form": form})
    else:
        return render(request, 'website/index.html')


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