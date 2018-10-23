from django.contrib import admin
from django.urls import path, include
import website

# handler404 = views.handle404

urlpatterns = [
    path('admin', admin.site.urls),
    path('', include('website.urls')),
]