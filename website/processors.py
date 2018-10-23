from django.conf import settings

def website_name(request):
    return {
        'website_name': settings.WEBSITE_NAME, 
        'website_base_name' : settings.WEBSITE_BASE_NAME,
        'captcha_site_key': settings.RECAPTHCA_SITE_KEY,
        'status_pending': settings.STATUS_PENDING,
        'status_declined': settings.STATUS_DECLINED,
        'status_approved': settings.STATUS_APPROVED,
    }