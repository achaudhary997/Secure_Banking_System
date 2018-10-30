from django.db import models
from django.contrib.auth.models import User
import random

def get_acc_num():
    # TODO generate number
    return random.sample(range(1000000000, 1600000000), 10)[random.randint(0, 9)]


# A single person can have multiple bank accounts though. They can be in the same bank or some external bank :/
# To access the multiple bank detials for a Profile p, just do p.account_set.objects.all() [Need to test this once]
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_profile")
    address = models.TextField(default="NONE", max_length=100)
    phone_number = models.CharField(default="NONE", max_length=15, blank=True) # validators should be a list
    otp_secret = models.CharField(default="NONE", max_length=16)

    # Info for KYC
    aadhar_number = models.CharField(
        default="NONE", max_length=15, blank=False)

    # Assign common permissions for all types of users

    class Meta:
        permissions = (
            ("add_transaction", "Create a New Transaction"),
        )
    
    def __str__(self):
        return "{}".format(self.user.username)


class CustomerIndividual(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_indi_customer")
    relationship_manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="indi_customer_rel_man")
    

    class Meta:
        permissions = (
            ("authorize_review", "Authorize review of Transactions"),
            ("initiate_info_mod", "Initiate information modification"),
            ("view_transaction", "View transaction details")
        )
    
    def __str__(self):
        return "{}".format(self.user.username)


class Merchant(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_merchant")
    relationship_manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="merchant_rel_man")

    class Meta:
        permissions = (
            ("authorize_review", "Authorize review of Transactions"),
            ("initiate_info_mod", "Initiate information modification"),
            ("view_transaction", "View transaction details")
        )

    def __str__(self):
        return "{}".format(self.user.username)

class Account(models.Model):
    acc_number = models.IntegerField(default=get_acc_num)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return "{}: {}: {}".format(self.user.user.username, self.acc_number, self.balance)
    
# Instead of reciever lets just keep the Account of the reciever
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    amount = models.FloatField(default=0.0)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    sender_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="sender_account")
    recipient_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account")
    signator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="signator") # change to integer and add sys manager signator
    timestamp = models.DateTimeField(auto_now_add=True)
    is_validated = models.IntegerField(default=0)
    transaction_mode = models.CharField(default="debit", max_length=20)
    
    @classmethod
    def create(self, amount, sender, recipient_account, sender_account, signator, is_validated, transaction_mode):
        transaction = self(amount=amount, sender=sender, recipient_account=recipient_account, sender_account=sender_account, signator=signator, is_validated=is_validated, transaction_mode=transaction_mode)
        return transaction
        

    def __str__(self):
        
        return "Transaction: " + str(self.timestamp)#+ self.sender.name + " -> " + self.receiver.name + ": " + str(self.amount) + " INR"

class ProfileModificationReq(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(default="NONE", max_length=100)
    phone_number = models.CharField(default="NONE", max_length=15, blank=True)
    is_verified_employee = models.IntegerField(default=0)
    is_verified_admin = models.IntegerField(default=0)

    @classmethod
    def create(self, user, address, phone_number, is_verified_admin, is_verified_employee):
        profile = self(user=user, address=address, phone_number=phone_number, is_verified_admin=is_verified_admin, is_verified_employee=is_verified_employee)

        return profile

    def __str__(self):
        return "User: " + str(self.user.username)

# 192.168.65.164:8000
# 192.168.59.27:8000
