from django.contrib import admin
from django.urls import path, include
import website

# handler404 = views.handle404
# handler404 = website.views.handler404

urlpatterns = [
    path('admin21232f297a57a5a743894a0e4a801fc3', admin.site.urls),
    path('', include('website.urls')),
]