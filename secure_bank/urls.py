from django.contrib import admin
from django.urls import path, include
import website

# handler404 = views.handle404
# handler404 = website.views.handler404

urlpatterns = [
    path('nimda_peru_inda', admin.site.urls),
    path('', include('website.urls')),
]