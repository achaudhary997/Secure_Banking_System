from django.conf import settings

def website_name(request):
    return {
        'website_name': settings.WEBSITE_NAME, 
        'captcha_site_key': settings.RECAPTHCA_SITE_KEY
    }