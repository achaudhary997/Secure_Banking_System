from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import requests
from .forms import LoginForm, RegisterForm, TransactionForm
from .models import Transaction, Profile, Account
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings

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
                    if result['success'] or not settings.CAPTCHA_VERIFICATION:
                        username = login_form.cleaned_data['username']
                        password = login_form.cleaned_data['password']

                        user = authenticate(request, username=username, password=password)

                        if user is not None:
                            login(request, user)
                            return redirect('home')
                        else:
                            messages.error(request, 'Incorrect Username or Password.')                        
                        return render(request, 'website/login.html')
                    else:
                        messages.error(request, 'Captcha Not Verified.')
                        return render(request, 'website/login.html')
        return render(request, 'website/login.html', context=None)
    else:
        return render(request, 'website/index.html', context=None)

def register_user(request):
    form = RegisterForm
    if not request.user.is_authenticated:
        if request.method == "POST":
            print("lol1")
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                print("lol2")
                recaptcha_response = request.POST.get('g-recaptcha-response')
                if recaptcha_response:
                    url = 'https://www.google.com/recaptcha/api/siteverify'
                    data = {
                        'secret' : '6LcqCWwUAAAAAC9-4iofBAthF8pwPHQlSg6n9w4O',
                        'response' : recaptcha_response
                    }
                    r = requests.post(url, data=data)
                    result = r.json()
                    if result['success'] or not settings.CAPTCHA_VERIFICATION:
                        user = register_form.save()
                        user.refresh_from_db()
                        
                        profile = Profile()
                        profile.user_id = user.id
                        profile.address = register_form.cleaned_data['address']
                        profile.phone_number = register_form.cleaned_data['contact']
                        profile.save()

                        email = register_form.cleaned_data['email_address']          
                        try:
                            match = User.objects.get(email=email)
                            print(match)
                            messages.error(request, "User with this email already exists.")
                            user.delete()
                            return render(request, 'website/register.html', context={"form": form})                            
                        except User.DoesNotExist:
                            pass
                        user.email = email
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
    form = TransactionForm
    if request.user.is_authenticated:
        if request.method == 'POST':
            print ("inside post")
            transact_form = TransactionForm(request.POST)
            if transact_form.is_valid():
                amount = transact_form.cleaned_data['amount']
                ifsccode = transact_form.cleaned_data['ifsc_code']
                accNum = transact_form.cleaned_data['acc_num']
                bankName = transact_form.cleaned_data['bank_name']

                recipientAccount = Account.objects.filter(accNumber=accNum).filter(ifsccode=ifsccode).filter(BankName=bankName)[0]
                print (type(recipientAccount).__name__)
                if recipientAccount is None:
                    return render(request, 'website/index.html')
                if float(amount) > 100000:
                    isValidated = False
                else:
                    isValidated = True
                
                recaptcha_response = request.POST.get('g-recaptcha-response')
                if recaptcha_response:
                    url = 'https://www.google.com/recaptcha/api/siteverify'
                    data = {
                        'secret': '6LcqCWwUAAAAAC9-4iofBAthF8pwPHQlSg6n9w4O',
                        'response': recaptcha_response
                    }
                    r = requests.post(url, data=data)
                    result = r.json()
                    if result['success']:
                        transaction = Transaction.create(   amount=amount, sender=request.user, 
                                                            recipientAccount=recipientAccount, 
                                                            isValidated=isValidated
                                                        )
                        transaction.save()
                        return render(request, 'website/transact.html')
                    else:
                        return render(request, 'website/transact.html', context={"form": form})

        return render(request, 'website/transact.html', context={'form':form})
    else:
        return render(request, 'website/index.html')
