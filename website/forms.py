from django import forms
from .models import Profile, Transaction, Account, ProfileModificationReq
from django.contrib.auth.models import User
import re

SEARCH_CHOICES = [
    ('user', 'Username'),
    ('acc_num', 'Account Number'),
    ('transaction_status', 'Transaction Status'),
    ('sent', 'Sent To (Account Number or Username)'),
    ('received', 'Received From (Account Number or Username)'),
    # ('date', 'Date')
]

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance.pk is None:
            self.empty_permitted = False # Here

    class Meta:
        model = Profile
        fields = ('__all__')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)


def get_acc_choices(user):
    profile = Profile.objects.filter(user=user)[0]
    accounts = Account.objects.filter(user=profile)
    acc_choices = []
    
    for account in accounts:
        acc_choices.append((str(account.acc_number), str(account.acc_number)))
        
    return acc_choices

class TransactionForm(forms.Form):
    
        
    amount = forms.FloatField(required=True)
    acc_num = forms.IntegerField(required=True)
    otp = forms.IntegerField(required=True)
    user_accounts = forms.CharField(widget=forms.Select(
        choices=SEARCH_CHOICES))
    

    def clean_acc_num(self):
        acc_num = self.cleaned_data['acc_num']
        if acc_num:
            if acc_num <= 0:
                raise forms.ValidationError("Invalid Account Number.")
        else:
            raise forms.ValidationError("Enter Account Number.")
        return acc_num
    
    def clean(self):
        transaction = self.cleaned_data
        try:
            recipientAccount = Account.objects.get(acc_number=transaction['acc_num'])
        except:
            raise forms.ValidationError("Account doesn't exist.")
        return transaction
    

class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email_address = forms.EmailField(required=True)
    password = forms.CharField(max_length=20, required=True)
    address = forms.CharField(max_length=100, required=True)
    contact = forms.CharField(max_length=15)
    aadhar_number = forms.CharField(max_length=12, required=True)

    class Meta:
        model = User
        fields = (  'username', 
                    'first_name', 
                    'last_name', 
                    'email_address', 
                    'password', 
                    'address', 
                    'contact',
                    'aadhar_number')

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if contact:
            if len(contact) > 15 or len(contact) < 9:
                raise forms.ValidationError("9-15 digits allowed.")
            elif not re.match('^\+?1?\d{9,15}$', contact):
                raise forms.ValidationError("Please Enter a valid contact number.")
        else:
            raise forms.ValidationError("Enter Contact Number.")
        return contact

    def clean_aadhar(self):
        aadhar_number = self.clean_data.get('aadhar_number')
        if aadhar_number:
            if len(aadhar_number != 12):
                raise forms.ValidationError("Invalid Aadhar Number")
        else:
            raise forms.ValidationError("Enter Aadhar Number")
        return aadhar_number

class ProfileUpdateForm(forms.ModelForm):
    address = forms.CharField(max_length=100, required=True)
    contact = forms.CharField(max_length=15)
    aadhar = forms.CharField(max_length=15)

    class Meta:
        model = ProfileModificationReq
        fields = (  'address',
                    'contact',
                    'aadhar')

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if contact:
            if len(contact) > 15 or len(contact) < 9:
                raise forms.ValidationError("9-15 digits allowed.")
            elif not re.match('^\+?1?\d{9,15}$', contact):
                raise forms.ValidationError(
                    "Please Enter a valid contact number.")
        else:
            raise forms.ValidationError("Enter Contact Number.")
        return contact

class SearchForm(forms.Form):
    search_parameter = forms.CharField(required=True, label='', 
                            widget=forms.TextInput(attrs={
                                    'placeholder': 'Search Here!',
                                    'class': 'form-control'
                                }))
    filter_type = forms.CharField(widget=forms.Select(choices=SEARCH_CHOICES), label='Filter')
