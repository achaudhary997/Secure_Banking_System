from django.contrib import admin
from django.urls import path, include
from . import views

handler404 = views.handle_404

urlpatterns = [
    path('', views.index, name="home"),
    # AUTH URLS

    path('profile.html', views.profile_user, name="profile"),
    path('login.jsp', views.login_user, name="login"),
    path('logout.aspx', views.logout_user, name="logout"),
    # path('register.php', views.register_user, name="register"),

    # TRANSACTION URLS

    path('transact.html', views.transact, name="transact"),
    path('manage_transaction.php', views.manage_transaction, name="manage_transaction"),
    path('history.html', views.history, name="history"),
    path('statement.pl', views.statement, name="get_statement"),
    path('approve.jsp', views.approve, name="approve_transaction"),

]
