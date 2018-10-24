from django.shortcuts import render, redirect, HttpResponseRedirect, render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
import requests
from .forms import LoginForm, RegisterForm, TransactionForm, ProfileUpdateForm, SearchForm
from .models import Transaction, Profile, Account, CustomerIndividual, Employee
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseNotFound
from .decorators import *
from itertools import chain
from django.http import HttpResponse
import csv
import pyotp
from random import randint
import pyqrcode

def handler404(request):
    return render(request, '404.html', status=404)


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
                            if check_otp_setup(user):
                                return redirect('home')
                            else:
                                return redirect('otp_setup')
                        else:
                            messages.error(request, 'Incorrect Username or Password.')
                        return render(request, 'website/login.html')
                    else:
                        messages.error(request, 'Captcha Not Verified.')
                        return render(request, 'website/login.html')
        return render(request, 'website/login.html', context=None)
    else:
        return render(request, 'website/index.html', context=None)


@login_required(login_url="/")
def otp_setup(request):
    if not check_otp_setup(request.user):
        secret=pyotp.random_base32()
        uri=pyotp.totp.TOTP(secret).provisioning_uri(str(request.user.username), issuer_name="GoldWomanSachs")
        profile = Profile.objects.filter(user=request.user)[0]
        print (profile)
        profile.otp_secret=secret
        profile.save()
        return render(request, 'website/otpsetup.html', context={"otp":uri})
    else:
        return redirect('home')


def check_otp_setup(user):
    profile = Profile.objects.filter(user=user)[0]
    if profile.otp_secret == "NONE":
        return False
    else:
        return True


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
                        profile.aadhar_number = register_form.cleaned_data['aadhar_number']
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
        if not check_otp_setup(request.user):
            return redirect('otp_setup')
        if request.method == 'POST':
            transact_form = TransactionForm(request.POST)
            if transact_form.is_valid():
                amount = transact_form.cleaned_data['amount']
                acc_num = transact_form.cleaned_data['acc_num']
                otp = transact_form.cleaned_data['otp']
                profile = Profile.objects.filter(user=request.user)[0]
                totp = pyotp.TOTP(profile.otp_secret)
                if not totp.verify(otp):
                    messages.error(
                        request, 'Tx Declined - Invalid OTP')
                    return render(request, 'website/transact.html')

                recipient_account = Account.objects.filter(acc_number=acc_num)[0]
                sender_account = Account.objects.filter(
                    user=User.objects.get(pk=request.user.id).user_profile.all()[0])[0]

                signator = CustomerIndividual.objects.filter(user=request.user)[0].relationship_manager

                print (type(recipient_account).__name__)
                if recipient_account is None:
                    return render(request, 'website/index.html')
                if recipient_account == sender_account:
                    messages.error(request, 'Tx Declined - Ha! You\'re smart, we\'re smarter.')
                    return render(request, 'website/transact.html')
                if float(amount) <= 0:
                    messages.error(request, 'Tx Declined - Ha! You\'re smart, we\'re smarter.')
                    return render(request, 'website/transact.html')
                if float(amount) > sender_account.balance - 10000:
                    is_validated = settings.STATUS_DECLINED
                    return render(request, 'website/transact.html')
                if float(amount) > 100000:
                    is_validated = settings.STATUS_PENDING
                else:
                    if amount < (sender_account.balance - 10000):
                        sender_account.balance -= amount
                        recipient_account.balance += amount
                        sender_account.save()
                        recipient_account.save()
                        is_validated = settings.STATUS_APPROVED
                    else:
                        #Return error saying atleast 10000 balance should be there
                        is_validated = settings.STATUS_DECLINED
                        messages.error(request, 'Tx Declined - You must maintain a minimum balance of INR 10,000.')
                        return render(request, 'website/transact.html')


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
                                                            recipient_account=recipient_account,
                                                            sender_account=sender_account,
                                                            signator=signator,
                                                            is_validated=is_validated
                                                        )
                        transaction.save()
                        return render(request, 'website/index.html')
                    else:
                        messages.error(
                            request, 'Invalid Captcha')
                        return render(request, 'website/transact.html', context={"form": form})

        return render(request, 'website/transact.html', context={'form':form})
    else:
        return render(request, 'website/index.html')

@login_required(login_url="/")
@group_required('System Manager', 'Employee')
def manage_transaction(request):
    if request.user.groups.filter(name='System Manager').exists():
        transactions = Transaction.objects.all()
    elif request.user.is_superuser:
        transactions = Transaction.objects.all()
    else:
        employee_object = Employee.objects.filter(user=request.user)[0]
        transactions = Transaction.objects.filter(signator=employee_object)

    pending_transactions = []
    approved_transactions = []

    search_form = SearchForm

    for transaction in transactions:
        if transaction.is_validated != settings.STATUS_PENDING:
            approved_transactions.append(transaction)
        else:
            pending_transactions.append(transaction)

    return render(  request, 
                    'website/manage_transactions.html', 
                    context={   "pending_transactions": pending_transactions, 
                                "approved_transactions": approved_transactions,
                                "search_form": search_form
                            }
                )

def profile_user(request):
    form = ProfileUpdateForm
    profile = request.user.id
    curr_user = User.objects.get(pk=request.user.id)

    profile = curr_user.user_profile.all()[0]
    user_name = curr_user.username
    user_address = profile.address
    user_ph = profile.phone_number
    aadhar = profile.aadhar
    user_details = {"username": user_name,
                    "address": user_address, "contact": user_ph, "aadhar": aadhar}
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
@group_required('Individual Customer', 'Merchant', 'System Manager', 'Employee')
def history(request):
    if request.user.is_authenticated:
        if not check_otp_setup(request.user):
            return redirect('otp_setup')
        sent_transactions = Transaction.objects.filter(sender=request.user)
        user_account = Account.objects.filter(
            user=User.objects.get(pk=request.user.id).user_profile.all()[0])[0]
        user_account_number = user_account.acc_number
        user_account_balance = user_account.balance
        received_transactions = Transaction.objects.filter(recipient_account=user_account)
        user_transactions = list(chain(sent_transactions, received_transactions))

        search_form = SearchForm

        return render(
                        request,
                        'website/history.html',
                        context={
                                    "user_transactions": user_transactions,
                                    "user_account_number": user_account_number,
                                    "user_account_balance": user_account_balance,
                                    "search_form": search_form
                                }
                    )

def check_valid_int(string):
    try:
        s = int(string)
        if s < 0:
            return False
        return True
    except ValueError:
        return False

@login_required(login_url="/")
@group_required('Individual Customer', 'Merchant')
def search(request):
    if request.method == "POST":
        if not check_otp_setup(request.user):
            return redirect('otp_setup')
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_parameter = search_form.cleaned_data['search_parameter']
            filter_type = search_form.cleaned_data['filter_type']

            sent_transactions = Transaction.objects.filter(sender=request.user)
            user_account = Account.objects.filter(
                                user=User.objects.get(pk=request.user.id).user_profile.all()[0])[0]
            user_account_number = user_account.acc_number
            user_account_balance = user_account.balance
            received_transactions = Transaction.objects.filter(recipient_account=user_account)
            user_transactions = list(chain(sent_transactions, received_transactions))

            filtered_transactions = list()

            if filter_type == "user":
                for transaction in user_transactions:
                    if transaction.sender.username == search_parameter or transaction.recipient_account.user.user.username == search_parameter:
                        filtered_transactions.append(transaction)
            elif filter_type == "acc_num":
                if check_valid_int(search_parameter):
                    search_parameter = int(search_parameter)
                    for transaction in user_transactions:
                        if transaction.sender_account.acc_number == search_parameter or transaction.recipient_account.acc_number == search_parameter:
                            filtered_transactions.append(transaction)
                else:
                    messages.error(request, "You're smart. But we're smarter.")
            # elif filter_type == "date":
            #     pass
            elif filter_type == "sent":
                if check_valid_int(search_parameter):
                    search_parameter = int(search_parameter)
                    for transaction in user_transactions:
                        if transaction.recipient_account.acc_number == search_parameter:
                            filtered_transactions.append(transaction)
                else:
                    for transaction in user_transactions:
                        if transaction.recipient_account.user.user.username == search_parameter:
                            filtered_transactions.append(transaction)
            elif filter_type == "received":
                if check_valid_int(search_parameter):
                    search_parameter = int(search_parameter)
                    for transaction in user_transactions:
                        if transaction.sender.acc_number == search_parameter:
                            filtered_transactions.append(transaction)
                else:
                    for transaction in user_transactions:
                        if transaction.sender.username == search_parameter:
                            filtered_transactions.append(transaction)
            elif filter_type == "transaction_status":
                tampered = False

                if search_parameter.lower() == "declined":
                    search_parameter = settings.STATUS_DECLINED
                elif search_parameter.lower() == "accepted" or search_parameter.lower() == "approved":
                    search_parameter = settings.STATUS_APPROVED
                elif search_parameter.lower() == "pending":
                    search_parameter = settings.STATUS_PENDING
                else:
                    messages.error(request, "You're smart. But we're smarter.")
                    tampered = True

                if not tampered:
                    for transaction in user_transactions:
                        if transaction.is_validated == search_parameter:
                            filtered_transactions.append(transaction)
            else:
                messages.error(request, "You're smart. But we're smarter.")
            return render(request, 'website/search.html', 
                context={
                    'filtered_transactions': filtered_transactions
                })
    return redirect('history')


@login_required(login_url="/")
@group_required('Individual Customer', 'Merchant')
def statement(request):

    sent_transactions = Transaction.objects.filter(sender=request.user)
    user_account = Account.objects.filter(
        user=User.objects.get(pk=request.user.id).user_profile.all()[0])[0]
    user_account_number = user_account.acc_number
    user_account_balance = user_account.balance
    received_transactions = Transaction.objects.filter(recipient_account=user_account)
    user_transactions = list(chain(sent_transactions, received_transactions))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="account_statement.csv"'

    writer = csv.writer(response)
    writer.writerow(['#', 'Sender Account', 'Recipient Account', 'Transaction Type', 'Amount', 'Timestamp', 'Transaction Status'])

    for transaction_counter in range(len(user_transactions)):
        transaction = user_transactions[transaction_counter]

        transaction_type = ""
        if user_account_number == transaction.sender_account.acc_number:
            transaction_type = "Debit"
        else:
            transaction_type = "Credit"

        validation_status = ""
        if transaction.is_validated == settings.STATUS_PENDING:
            validation_status = "Pending"
        elif transaction.is_validated == settings.STATUS_DECLINED:
            validation_status = "Declined"
        elif transaction.is_validated == settings.STATUS_APPROVED:
            validation_status = "Approved"

        writer.writerow([str(transaction_counter + 1),
                        transaction.sender_account.acc_number,
                        transaction.recipient_account.acc_number,
                        transaction_type,
                        str(transaction.amount),
                        transaction.timestamp,
                        validation_status])

    return response


@login_required(login_url="/")
@group_required('System Manager', 'Employee')
def approve(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            if request.POST.get("approve_transaction"):
                transaction_id = request.POST['transaction_id']
                if not transaction_id.isdigit():
                    messages.error(messages.
                        request, 'Dont tamper with the request -_-')
                    return render(request, 'website/manage_transactions.html')
                try:
                    transaction = Transaction.objects.filter(transaction_id=transaction_id)[0]
                except:
                    messages.error(
                        request, 'Dont tamper with the request -_-')
                    return render(request, 'website/manage_transactions.html')
                
                sender_account = transaction.sender_account
                recipient_account = transaction.recipient_account
                amount = transaction.amount
                sender_account.balance -= amount
                recipient_account.balance += amount
                sender_account.save()
                recipient_account.save()
                transaction.is_validated = settings.STATUS_APPROVED
                transaction.save()
                
            elif request.POST.get("decline_transaction"):
                transaction_id = request.POST['transaction_id']
                if not transaction_id.isdigit():
                    messages.error(
                        request, 'Dont tamper with the request -_-')
                    return render(request, 'website/manage_transactions.html')
                try:
                    transaction = Transaction.objects.filter(transaction_id=transaction_id)[0]
                except:
                    messages.error(
                        request, 'Dont tamper with the request -_-')
                    return render(request, 'website/manage_transactions.html')
        
                transaction.is_validated = settings.STATUS_DECLINED
                transaction.save()

            return HttpResponseRedirect('manage_transaction.php')
        else:
            return render('website/manage_transactions.html')
    else:
        return render('website/login.html')

