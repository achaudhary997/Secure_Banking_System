from django.shortcuts import render, redirect, HttpResponseRedirect, render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
import requests
from .forms import LoginForm, RegisterForm, TransactionForm, ProfileUpdateForm, SearchForm, InternalProfileUpdateForm
from .models import Transaction, Profile, Account, CustomerIndividual, ProfileModificationReq
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
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from base64 import b64decode

# LOGGING ############
import os, sys
import logging, logging.config

# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'stream': sys.stdout,
#         }
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'DEBUG'
#     }
# }
# logging.config.dictConfig(LOGGING)
# logging.info("HELLO")
#######################

def handler404(request):
    return render(request, '404.html', status=404)


def index(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=request.user.id)
        if profile.first_login:
            private_key_string = profile.private_key
            edited1 = private_key_string
            if private_key_string[31] != '\n':
                edited1 = private_key_string[:31] + '\n' + private_key_string[31:]
            
            end_index = edited1.find("-----END")
            edited2 = edited1[:end_index] + '\n' + edited1[end_index:]

            private_key = RSA.importKey(edited2)
            public_key = private_key.publickey().exportKey().decode("utf-8")

            profile.first_login = False
            profile.save()

            return render(request, 'website/index.html', context={
                    "public_key": public_key
                })

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
                        'secret' : settings.RECAPTCHA_SECRET,
                        'response' : recaptcha_response
                    }
                    r = requests.post(url, data=data)
                    result = r.json()
                    if result['success'] or not settings.CAPTCHA_VERIFICATION:
                        username = login_form.cleaned_data['username']
                        password = login_form.cleaned_data['password']

                        all_users = User.objects.all()
                        selected_user = None

                        for user in all_users:
                            if user.username == username:
                                selected_user = user

                        if selected_user:
                            if not selected_user.is_active:
                                messages.error(request, 'User Account has been suspended. Please contact Admin.')
                                return render(request, 'website/login.html', context={'form': login_form})

                        user = authenticate(request, username=username, password=password)

                        if user is not None:
                            login(request, user)
                            if not check_otp_setup(request.user):
                                return redirect('otp_setup')
                            else:
                                return redirect('home')
                        else:
                            messages.error(request, 'Incorrect Username or Password.')
                            return render(request, 'website/login.html', context={'form': login_form})
                    else:
                        messages.error(request, 'Captcha not verified')
                        return render(request, 'website/login.html', context={'form': login_form})
                else:
                    messages.error(request, 'Captcha not verified')
                    return render(request, 'website/login.html', context={'form': login_form})
        return render(request, 'website/login.html', context=None)
    else:
        return render(request, 'website/index.html', context=None)


@login_required(login_url="/login.html")
def otp_setup(request):
    if not check_otp_setup(request.user):
        secret=pyotp.random_base32()
        uri=pyotp.totp.TOTP(secret).provisioning_uri(str(request.user.username), issuer_name="GoldWomanSachs")
        profile = Profile.objects.filter(user=request.user)[0]
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
                            messages.error(request, "User with this email already exists.")
                            user.delete()
                            return render(request, 'website/register.html', context={'form': register_form})
                        except User.DoesNotExist:
                            pass
                        user.email = email
                        user.set_password(register_form.cleaned_data['password'])
                        user.save()
                        login(request, user)
                        return redirect('home')
                else:
                    messages.error(request, 'Captcha not verified')
                    return render(request, 'website/register.html', context={'form': register_form})
        return render(request, 'website/register.html', context={"form": form})
    else:
        return render(request, 'website/index.html')

@login_required(login_url="/login.html")
def logout_user(request):
    logout(request)
    return render(request, 'website/index.html', context=None)


def get_acc_choices(user):
    profile = Profile.objects.filter(user=user)[0]
    accounts = Account.objects.filter(user=profile)
    acc_choices = []

    for account in accounts:
        acc_choices.append((str(account.acc_number), str(account.balance), "Account Number: " + str(account.acc_number) + ', Balance: ' + str(account.balance)))

    return acc_choices


def clean_priv_key(private_key_string):
    edited1 = private_key_string
    if private_key_string[31] != '\n':
        edited1 = private_key_string[:31] + '\n' + private_key_string[31:]
    
    end_index = edited1.find("-----END")
    edited2 = edited1[:end_index] + '\n' + edited1[end_index:]
    return edited2


def myDecrypt(privateKey, ciphertext):
	try:
		key = RSA.importKey(privateKey)
		cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
		decrypted_message = cipher.decrypt(b64decode(ciphertext))
		return decrypted_message
	except ValueError:
		# TODO: Handle this error in the website
		return settings.INVALID_PRIVATE_KEY
	except TypeError:
		return settings.TAMPERED_PRIVATE_KEY


@login_required(login_url="/login.html")
@active_account_required
def transact(request):
    form = TransactionForm
    if not check_otp_setup(request.user):
        return redirect('otp_setup')

    user_accounts = get_acc_choices(request.user)
    if request.method == 'POST':
        print("IN")
        transact_form = TransactionForm(request.POST, request=request)
        if transact_form.is_valid():
            print("IN2")
            # logging.info("FORM_VALID")
            amount = transact_form.cleaned_data['amount']
            acc_num = transact_form.cleaned_data['acc_num']
            otp = transact_form.cleaned_data['otp']
            user_account = transact_form.cleaned_data['user_accounts']
            transaction_type = transact_form.cleaned_data['transaction_mode']
            public_key = transact_form.cleaned_data['public_key']
            encrypted = transact_form.cleaned_data['encrypted']

            print(encrypted)
            user_private_key = clean_priv_key(request.user.user_profile.private_key)
            decrypted = myDecrypt(user_private_key, encrypted)
            if decrypted == settings.INVALID_PRIVATE_KEY:
                messages.error(
                    request, 'Tx Declined - Key Error')
                return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})
            elif decrypted == settings.TAMPERED_PRIVATE_KEY:
                messages.error(
                    request, 'Tx Declined - Tampering detected.')
                return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})
            print(decrypted)


            profile = Profile.objects.filter(user=request.user)[0]
            totp = pyotp.TOTP(profile.otp_secret)
            # logging.info("BEFOREOTP")
            if not totp.verify(otp):
                messages.error(
                    request, 'Tx Declined - Invalid OTP')
                return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})


            recipient_account = Account.objects.filter(acc_number=acc_num)[0]
            sender_account = Account.objects.filter(acc_number=user_account)[0]
            signator = CustomerIndividual.objects.filter(user=request.user)[0].relationship_manager
            
            sender_is_merchant = request.user.groups.filter(name="Merchant").exists()
            recipient_is_merchant = recipient_account.user.user.groups.filter(name="Merchant").exists()

            if signator:
                if recipient_account is None:
                    messages.error(request, 'Tx Declined - Please enter a valid account number.')
                    return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})
                
                
                if transaction_type == "transfer":
                    if recipient_account == sender_account:
                        messages.error(request, 'Tx Declined - Ha! You\'re smart, we\'re smarter. You cannot send money to the same account')
                        return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})
                else: 
                    if recipient_account != sender_account:
                        messages.error(
                            request, 'Account number must be your own for withdrawal/deposit')
                        return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})


                if float(amount) <= 0:
                    messages.error(request, 'Tx Declined - Ha! You\'re smart, we\'re smarter. No negative amounts allowed.')
                    return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})


                if float(amount) > sender_account.balance - 10000:
                    messages.error(request, "Tx Declined. This transaction will result in account balance below minimum threshold")
                    return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})


                if float(amount) > 100000 and transaction_type == "debit" or transaction_type == "credit":
                    is_validated = settings.STATUS_PENDING
                    if recipient_is_merchant and sender_account != recipient_account:
                        is_validated = settings.STATUS_MERCHANT_PENDING
                elif transaction_type == "transfer" and recipient_is_merchant and sender_account != recipient_account:
                    is_validated = settings.STATUS_MERCHANT_PENDING
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
                        return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})

                transaction = Transaction.create(   amount=amount, sender=request.user,
                                                    recipient_account=recipient_account,
                                                    sender_account=sender_account,
                                                    signator=signator,
                                                    is_validated=is_validated,
                                                    transaction_mode=transaction_type
                                                )
                transaction.save()
                return render(request, 'website/index.html')
            else:
                messages.error(request, 'No Relationship Manager assigned. Please contact Admin')
                return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})
        else:
            # logging.info("FORM_INVALID")
            # print (transact_form.errors)
            print("HEREBOI", str(transact_form.errors))
            # logging.info(transact_form.errors)
            return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})

    return render(request, 'website/transact.html', context={"form": form, "user_accounts": user_accounts})

@login_required(login_url="/login.html")
@group_required('System Manager', 'Employee')
def manage_transaction(request):
    if request.user.groups.filter(name='System Manager').exists():
        transactions = Transaction.objects.all()
    elif request.user.is_superuser:
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(signator=request.user)

    pending_transactions = []
    approved_transactions = []
    declined_transactions = []

    search_form = SearchForm

    for transaction in transactions:
        if transaction.is_validated == settings.STATUS_PENDING:
            pending_transactions.append(transaction)
        elif transaction.is_validated == settings.STATUS_DECLINED:
            declined_transactions.append(transaction)
        else:
            approved_transactions.append(transaction)

    return render(  request, 
                    'website/manage_transactions.html', 
                    context={   "pending_transactions": pending_transactions, 
                                "approved_transactions": approved_transactions,
                                "declined_transactions":declined_transactions,
                                "search_form": search_form
                            }
                )

def profile_user(request):
    form = ProfileUpdateForm
    profile = request.user.id
    curr_user = User.objects.get(pk=request.user.id)

    profile = Profile.objects.filter(user=curr_user)[0]
    user_name = curr_user.username
    user_address = profile.address
    user_ph = profile.phone_number
    aadhar = profile.aadhar_number

    user_details = {"username": user_name,
                    "address": user_address, "contact": user_ph, "aadhar": aadhar}
    print ("Function running")
    if request.method == 'POST':
        profile_update_form = ProfileUpdateForm(request.POST)
        print ("Might not be valid")
        if profile_update_form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            print ("YES VALID")
            if recaptcha_response:
                url = 'https://www.google.com/recaptcha/api/siteverify'
                data = {
                    'secret' : settings.RECAPTCHA_SECRET,
                    'response' : recaptcha_response
                }
                r = requests.post(url, data=data)
                result = r.json()
                if result['success'] or not settings.CAPTCHA_VERIFICATION:
                    profile = ProfileModificationReq(
                            user=curr_user, 
                            address=profile_update_form.cleaned_data['address'], 
                            phone_number=profile_update_form.cleaned_data['contact'], 
                            is_verified_admin=settings.STATUS_PENDING, 
                            is_verified_employee=settings.STATUS_PENDING
                        )
                    profile.save()
                    return render(request, 'website/profile.html', context=user_details)
                else:
                    messages.error(request, 'Captcha not verified')
                    user_details["form"] = profile_update_form
                    return render(request, 'website/profile.html', context={user_details})# user_details})
            else:
                messages.error(request, 'Captcha not verified')
                user_details["form"] = profile_update_form
                return render(request, 'website/profile.html', context={user_details})# user_details})                   
        else:
            return render(request, 'website/profile.html', context=user_details)
    else:
        print ("HERE")
        return render(request, 'website/profile.html', context=user_details)


@login_required(login_url="/login.html")
@group_required('Individual Customer', 'Merchant', 'System Manager', 'Employee')
def history(request):
    if request.user.is_authenticated:
        if not check_otp_setup(request.user):
            return redirect('otp_setup')
        user_transactions = Transaction.objects.filter(sender=request.user)
        user_account = Account.objects.filter(
            user=Profile.objects.filter(user=request.user)[0])
        user_account_details = []
        for account in user_account:
            user_account_details.append([account.acc_number, account.balance])
            user_transactions = list(
                chain(user_transactions, Transaction.objects.filter(recipient_account=account)))
        user_transactions = list(set(user_transactions))
        for transaction in user_transactions:
            sender_account = transaction.sender_account
            recipient_account = transaction.recipient_account
            if recipient_account in user_account and sender_account not in user_account:
                transaction.transaction_mode = "transfer - credit"
            elif recipient_account not in user_account and sender_account in user_account:
                transaction.transaction_mode = "transfer - debit"
            elif recipient_account in user_account and sender_account in user_account and recipient_account != sender_account:
                transaction.transaction_mode = "transfer - within accounts"

        print (user_transactions)

        search_form = SearchForm

        return render(
                        request,
                        'website/history.html',
                        context={
                            "user_transactions": user_transactions,
                            "user_account_details": user_account_details,
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

@login_required(login_url="/login.html")
@group_required('Individual Customer', 'Merchant', 'System Manager', 'Employee')
def search(request):
    manager_group = False
    if request.method == "POST":
        if not check_otp_setup(request.user):
            return redirect('otp_setup')
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_parameter = search_form.cleaned_data['search_parameter']
            filter_type = search_form.cleaned_data['filter_type']

            user_transactions = []

            if request.user.groups.filter(name='Individual Customer').exists() or request.user.groups.filter(name='Merchant').exists():
                sent_transactions = Transaction.objects.filter(sender=request.user)
                user_account = Account.objects.filter(
                    user=Profile.objects.filter(user=request.user)[0])[0]
                user_account_number = user_account.acc_number
                user_account_balance = user_account.balance
                received_transactions = Transaction.objects.filter(recipient_account=user_account)
                user_transactions = list(chain(sent_transactions, received_transactions))

            elif request.user.groups.filter(name='System Manager').exists() or request.user.groups.filter(name='Employee').exists():
                manager_group = True
                if request.user.groups.filter(name='System Manager').exists():
                    user_transactions = Transaction.objects.all()
                elif request.user.is_superuser:
                    user_transactions = Transaction.objects.all()
                else:
                    
                    user_transactions = Transaction.objects.filter(signator=request.user)

            else:
                messages.error(request, "You're smart; We're Smarter")
                return redirect('home')
            
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
    if manager_group:
        return redirect('manage_transaction')
    else:
        return redirect('history')

#CHECK WHETHER USER_PROFILE.ALL WORKS
@login_required(login_url="/login.html")
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


@login_required(login_url="/login.html")
@group_required('System Manager', 'Employee')
def approve(request):
    if request.method == 'POST':
        if request.POST.get("approve_transaction"):
            transaction_id = request.POST['transaction_id']
            if not transaction_id.isdigit():
                messages.error(messages.
                    request, 'Dont tamper with the request -_-')
                return render(request, 'website/manage_transactions.html', context={'messages': messages})
            try:
                transaction = Transaction.objects.filter(transaction_id=transaction_id)[0]
            except:
                messages.error(
                    request, 'Dont tamper with the request -_-')
                return render(request, 'website/manage_transactions.html', context={'messages': messages})
            
            sender_account = transaction.sender_account
            recipient_account = transaction.recipient_account
            amount = transaction.amount
            validation = "valid"
            if transaction.transaction_mode == "transfer":
                if sender_account.balance - amount > 10000:
                    sender_account.balance -= amount
                    recipient_account.balance += amount
                    sender_account.save()
                    recipient_account.save()
                else:
                    validation = "invalid"
            elif transaction.transaction_mode == "debit":
                if sender_account.balance - amount > 10000:
                    sender_account.balance -= amount
                    sender_account.save()
                else:
                    validation = "invalid"
            elif transaction.transaction_mode == "credit":
                sender_account.balance += amount
                sender_account.save()
            
            if validation == "invalid":
                messages.error(messages.
                               request, 'Approving this request would lead to balance amount less than threshold. Transaction has been automatically declined.')
                return render(request, 'website/manage_transactions.html', context={'messages': messages})
                transaction.is_validated = settings.STATUS_DECLINED
            else:
                transaction.is_validated = settings.STATUS_APPROVED
            transaction.signator = request.user
            transaction.save()

        elif request.POST.get("decline_transaction"):
            transaction_id = request.POST['transaction_id']
            if not transaction_id.isdigit():
                messages.error(
                    request, 'Dont tamper with the request -_-')
                return render(request, 'website/manage_transactions.html', context={'messages': messages})
            try:
                transaction = Transaction.objects.filter(transaction_id=transaction_id)[0]
            except:
                messages.error(
                    request, 'Dont tamper with the request -_-')
                return render(request, 'website/manage_transactions.html', context={'messages': messages})
    
            transaction.is_validated = settings.STATUS_DECLINED
            transaction.signator = request.user
            transaction.save()

        return HttpResponseRedirect('manage_transaction.php')
    else:
        return render(request, 'website/manage_transactions.html')


@login_required(login_url="/login.html")
def profile_mod_approve(request):
    profile_reqs = ProfileModificationReq.objects.all()
    profile_mods = []
    if request.user.groups.filter(name='Employee').exists():
        for req in profile_reqs:
            if req.is_verified_employee == settings.STATUS_PENDING and CustomerIndividual.objects.filter(user=req.user)[0].relationship_manager == request.user:
                profile_mods.append(req)
        return render(request, 'website/manage_profiles.html', context={'profiles' : profile_mods})
    elif request.user.groups.filter(name='System Administrator').exists():
        for req in profile_reqs:
            if req.is_verified_employee == settings.STATUS_APPROVED:
                profile_mods.append(req)
        internal_user_accounts = get_internal_accounts(request)
        print (profile_mods)
        return render(request, 
        'website/account_modification.html', 
        context={'internal_accounts': internal_user_accounts, 'external_accounts': profile_mods})


def get_internal_accounts(request):
    internal_user_accounts = []
    all_users = User.objects.all()
    print (all_users)
    for user in all_users:
        if user != request.user:
            if user.groups.filter(name='Employee').exists():
                internal_user_accounts.append(
                    (str(user.pk), str(user.username), str(user.username) + ' - ' + "Employee"))
            elif user.groups.filter(name='System Manager').exists():
                internal_user_accounts.append(
                    (str(user.pk), str(user.username), str(user.username) + ' - ' + "System Manager"))
    return internal_user_accounts


# SYSTEM ADMIN VIEWS

@login_required(login_url="/login.html")
@group_required('System Administrator')
def account_modify(request):
    internal_user_accounts = get_internal_accounts(request)
    
    print (internal_user_accounts)
    return render(request, 'website/account_modification.html', context={'internal_accounts': internal_user_accounts})


@login_required(login_url="/login.html")
@group_required('System Administrator', 'Employee')
def approve_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            print ("inside here")
            if request.POST.get("approve_profile_mod_request"):
                profile = ProfileModificationReq.objects.filter(id=request.POST['profile_id'])[0]
                if request.user.groups.filter(name='Employee').exists():
                    profile.is_verified_employee = settings.STATUS_APPROVED
                    profile.save()
                elif request.user.groups.filter(name='System Administrator').exists():
                    profile.is_verified_admin = settings.STATUS_APPROVED
                    user_profile = Profile.objects.filter(user=profile.user)[0]
                    user_profile.address = profile.address
                    user_profile.phone_number = profile.phone_number
                    user_profile.save()
                    profile.delete()



            elif request.POST.get("decline_profile_mod_request"):
                profile = ProfileModificationReq.objects.filter(
                    id=request.POST['profile_id'])[0]
                if request.user.groups.filter(name='Employee').exists():
                    profile.delete()
                elif request.user.groups.filter(name='System Administrator').exists():
                    profile.delete()

            return HttpResponseRedirect('accountmod.php')
        else:
            return render(request, 'website/manage_profiles.html')
    else:
        return render(request, 'website/index.html', context=None)


@login_required(login_url="/login.html")
@group_required('System Administrator')
def internal_account_mod(request):
    if request.user.is_authenticated:
        form = InternalProfileUpdateForm
        if request.method == 'POST':
            profile_update_form = InternalProfileUpdateForm(request.POST)
            if profile_update_form.is_valid():
                user_id = profile_update_form.cleaned_data['user_account']
                print (user_id)
                user_address = profile_update_form.cleaned_data['address']
                user_ph = profile_update_form.cleaned_data['contact']
                cur_user = User.objects.filter(id=user_id)[0]
                print (cur_user)
                user_profile = Profile.objects.filter(user=User.objects.filter(id=user_id)[0])[0]
                user_profile.address = user_address
                user_profile.phone_number = user_ph
                user_profile.save()
                return render(request, 'website/index.html', context=None)
            else:
                return render(request, 'website/index.html', context=None)
        else:
            return render(request, 'website/index.html', context=None)
    else:
        return render(request, 'website/index.html', context=None)


@login_required(login_url="/login.html")
@group_required('System Administrator')
def suspend_account(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user = request.user
            user.is_active = False
            user.save()
        return render(request, 'website/manage_profiles.html')
    return render(request, 'website/index.html', context=None)


def get_received_payments(request):
    transactions = Transaction.objects.filter(is_validated=settings.STATUS_MERCHANT_PENDING)
    print (transactions)
    received_payments = []

    user_accounts = Account.objects.filter(user=Profile.objects.filter(user=request.user)[0])

    for transaction in transactions:
        if transaction.recipient_account in user_accounts:
            received_payments.append(transaction)

    return received_payments


@login_required(login_url="/login.html")
@group_required('Merchant')
def received_payment(request):
    if request.user.is_authenticated:
        received_payments = get_received_payments(request)
        print (received_payments)
        return render(request, 'website/pending_payment.html', context={"received_payments" : received_payments})

    return render(request, 'website/index.html', context=None)



@login_required(login_url="/login.html")
@group_required('Merchant')
def forward_payment(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            transaction_id = request.POST['transaction_id']
            if not transaction_id.isdigit():
                messages.error(messages.
                                request, 'Dont tamper with the request -_-')
                return render(request, 'website/manage_transactions.html', context={'messages': messages})
            try:
                transaction = Transaction.objects.filter(
                    transaction_id=transaction_id)[0]
            except:
                messages.error(
                    request, 'Dont tamper with the request -_-')
                return render(request, 'website/manage_transactions.html', context={'messages': messages})
            if request.POST.get("forward_payment"):
                transaction.is_validated = settings.STATUS_PENDING
                transaction.save()
            elif request.POST.get("decline_payment"):
                transaction.is_validated = settings.STATUS_DECLINED
                transaction.save()
        return render(request, 'website/pending_payment.html', context={"received_payments": get_received_payments(request)})

    return render(request, 'website/index.html', context=None)
