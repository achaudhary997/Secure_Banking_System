from django.contrib.auth.decorators import user_passes_test
from .models import Transaction, Profile, Account, CustomerIndividual, Merchant

def group_required(*group_names):
    
    def in_groups(user):
        if user.is_authenticated:
            print (user.groups.values_list())
            if user.is_superuser or (user.groups.values_list()[0][1] in group_names):
                return True
        return False
    
    return user_passes_test(in_groups)

