from django.shortcuts import render, redirect
from django.contrib import messages
import requests

# # Create your views here.
def login(request):
    
    if request.method == 'POST':
        form = # form name
        if form.is_valid():
        recaptchaResponse = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret' : '6LcqCWwUAAAAAC9-4iofBAthF8pwPHQlSg6n9w4O' any better place to store this?,
            'response' : recaptchaResponse
        }
        r = requests.post(url, data=data)
        result = r.json()
        if result['success']:
            # username password validation
            return render(request, 'website/login.html') # Got to change this to dashboard or smth
        else:
            return render(request, 'website/login.html')
            

        
