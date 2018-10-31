from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from .models import Transaction, Profile, Account, CustomerIndividual, Merchant

def group_required(*group_names):
    
    def in_groups(user):
        if user.is_authenticated:
            print (user.groups.values_list())
            if user.is_superuser or (user.groups.values_list()[0][1] in group_names):
                return True
        return False
    
    return user_passes_test(in_groups)


def active_account_required(function):

    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_active:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


