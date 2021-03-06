from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views

# handler404 = views.handle_404
# handler404 = 'website.views.handle404'
handler404 = views.handler404


urlpatterns = [
    path('', views.index, name="home"),

    #admin ops URLS
    path('accountmod.php', views.profile_mod_approve, name="account_mod"),
    path('approve.lsp', views.approve_profile, name="approve_profile"),
    path('approve.psp', views.internal_account_mod, name="internal_account_mod"),
    path('suspend.lol', views.suspend_account, name="suspend_account"),

    #OTP Setup URL
    path('otpsetup.cgi.bin', views.otp_setup, name="otp_setup"),
    
    # AUTH URLS

    path('profile.html', views.profile_user, name="profile"),
    path('logout.aspx', views.logout_user, name="logout"),
    path('login.html', views.login_user, name="login"),

    # TRANSACTION URLS

    path('transact.html', views.transact, name="transact"),
    path('manage_transaction.php', views.manage_transaction, name="manage_transaction"),
    path('history.html', views.history, name="history"),
    path('search.aspx', views.search, name="search"),
    path('statement.pl', views.statement, name="get_statement"),
    path('approve.jsp', views.approve, name="approve_transaction"),
    path('forward_payment.hmm', views.forward_payment, name="forward_payment"),
    path('received_payment.hmm', views.received_payment, name="received_payment"),


]
