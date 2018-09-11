from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names):
    
    def in_groups(user):
        if user.is_authenticated:
            if (user.groups.values_list()[0][1] in group_names) or user.is_superuser:
                return True
        return False
    
    return user_passes_test(in_groups)