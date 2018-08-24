from django import forms
from .models import Profile


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance.pk is None:
            self.empty_permitted = False # Here

    class Meta:
        model = Profile
        fields = ('__all__')

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    # password = forms.PasswordInput()