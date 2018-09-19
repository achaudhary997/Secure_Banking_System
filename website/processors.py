from django.conf import settings

def website_name(request):
    return {'website_name': settings.WEBSITE_NAME}