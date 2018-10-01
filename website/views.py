from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import requests
from .forms import LoginForm, RegisterForm, TransactionForm, ProfileUpdateForm
from .models import Transaction, Profile, Account, CustomerIndividual, Employee
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import *
from itertools import chain

def handle_404(request):
    return render(request, 'website/404.html', staus=404)


def index(request):
    return render(request, 'website/index.html', context=None)

def login_user(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            login_form = LoginForm(request.POST)
            if login_form.is_valid():  
                recaptcha_response = request.POST.get('g-recaptcha-response')
                print("hello")
                if recaptcha_response:
                    url = 'https://www.google.com/recaptcha/api/siteverify'
                    data = {
                        'secret' : settings.RECAPTCHA_SECRET,
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
                        'secret' : settings.RECAPTCHA_SECRET,
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
            transact_form = TransactionForm(request.POST)
            if transact_form.is_valid():
                amount = transact_form.cleaned_data['amount']
                acc_num = transact_form.cleaned_data['acc_num']

                recipientAccount = Account.objects.filter(acc_number=acc_num)[0]
                senderAccount = Account.objects.filter(
                    user=User.objects.get(pk=request.user.id).user_profile.all()[0])[0]
                
                signator = CustomerIndividual.objects.filter(user=request.user)[0].relationship_manager

                print (type(recipientAccount).__name__)
                if recipientAccount is None:
                    return render(request, 'website/index.html')
                if float(amount) > 100000:
                    isValidated = False
                else:
                    if amount < senderAccount.balance - 10000:
                        senderAccount.balance -= amount
                        recipientAccount.balance += amount
                        senderAccount.save()
                        recipientAccount.save()
                        isValidated = True
                    else:
                        #Return error saying atleast 10000 balance should be there
                        isValidated = False
                    
                
                recaptcha_response = request.POST.get('g-recaptcha-response')
                if recaptcha_response:
                    url = 'https://www.google.com/recaptcha/api/siteverify'
                    data = {
                        'secret': settings.RECAPTCHA_SECRET,
                        'response': recaptcha_response
                    }
                    r = requests.post(url, data=data)
                    result = r.json()
                    if result['success']:
                        transaction = Transaction.create(   amount=amount, sender=request.user, 
                                                            recipientAccount=recipientAccount, 
                                                            senderAccount=senderAccount,
                                                            signator=signator,
                                                            isValidated=isValidated
                                                        )
                        transaction.save()
                        return render(request, 'website/transact.html')
                    else:
                        return render(request, 'website/transact.html', context={"form": form})

        return render(request, 'website/transact.html', context={'form':form})
    else:
        return render(request, 'website/index.html')

@login_required(login_url="/")
@group_required('System Manager', 'Employee')
def manage_transaction(request):
    if request.user.groups.filter(name='System Manager').exists():
        transactions = Transaction.objects.all()
    else:
        employee_object = Employee.objects.filter(user=request.user)[0]
        transactions = Transaction.objects.filter(signator=employee_object)

    return render(request, 'website/manage_transactions.html', context={"all_transactions": transactions})
def profile_user(request):
    form = ProfileUpdateForm
    profile = request.user.id
    curr_user = User.objects.get(pk=request.user.id)

    profile = curr_user.user_profile.all()[0]
    user_name = curr_user.username
    user_address = profile.address
    user_ph = profile.phone_number
    user_details = {"username": user_name,
                    "address": user_address, "contact": user_ph}
    if request.user.is_authenticated:
        if request.method == 'POST':
            profile_update_form = ProfileUpdateForm(request.POST)
            if profile_update_form.is_valid():
                profile = profile_update_form.save(commit=False)
                profile.user = request.user
                profile.save()
                return render(request, 'website/profile.html', context=user_details)
            else:
                return render(request, 'website/profile.html', context=user_details)
        else:
            
            return render(request, 'website/profile.html', context=user_details)
    else:       
        return render(request, 'website/login.html', context=None)


@login_required(login_url="/")
@group_required('Individual Customer', 'Merchant')
def history(request):
    sent_transactions = Transaction.objects.filter(sender=request.user)
    user_account = Account.objects.filter(
        user=User.objects.get(pk=request.user.id).user_profile.all()[0])[0]
    user_account_number = user_account.acc_number
    user_account_balance = user_account.balance
    received_transactions = Transaction.objects.filter(recipientAccount=user_account)
    user_transactions = list(chain(sent_transactions, received_transactions))
    return render(  
                    request, 
                    'website/history.html', 
                    context={   
                                "user_transactions": user_transactions, 
                                "user_account_number": user_account_number, 
                                "user_account_balance": user_account_balance
                            }
                )
