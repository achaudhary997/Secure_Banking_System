from django import forms
from .models import Profile, Transaction
from django.contrib.auth.models import User
import re

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

class TransactionForm(forms.ModelForm):
    amount = forms.FloatField(required=True, min_value=0)
    ifsccode = forms.CharField(required=True)
    accNum = forms.IntegerField(required=True)
    bankName = forms.CharField(required=True)
    
    def clean_transaction(self):
        contact = self.cleaned_data.get('contact')


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email_address = forms.EmailField(required=True)
    password = forms.CharField(max_length=20, required=True)
    address = forms.CharField(max_length=100, required=True)
    contact = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = (  'username', 
                    'first_name', 
                    'last_name', 
                    'email_address', 
                    'password', 
                    'address', 
                    'contact')

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
