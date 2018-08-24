from django.contrib import admin
from .models import Profile, Transaction
from .forms import UserProfileForm
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

class UserProfileInline(admin.TabularInline):
    model = Profile
    form = UserProfileForm


class UserAdmin(DjangoUserAdmin):
    inlines = [ UserProfileInline,]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Transaction)