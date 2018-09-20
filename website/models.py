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

    # Info for KYC
    # Assign common permissions for all types of users

    class Meta:
        permissions = (
            ("add_transaction", "Create a New Transaction"),
        )

# Have to add inheritence for atleast address or phone number

class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_employee")
    class Meta:
        permissions = (
            ("delete_transaction", "Delete a transaction"),      
        )                                    

class SystemManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_sys_manager")


    class Meta:
        permissions = (
            ("auth_crit_trans", "Authorize Critical Transaction"),
        )

class CustomerIndividual(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_indi_customer")

    class Meta:
        permissions = (
            ("authorize_review", "Authorize review of Transactions"),
            ("initiate_info_mod", "Initiate information modification"),
            ("view_transaction", "View transaction details")
        )


class Merchant(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_merchant")
    
    class Meta:
        permissions = (
            ("authorize_review", "Authorize review of Transactions"),
            ("initiate_info_mod", "Initiate information modification"),
            ("view_transaction", "View transaction details")
        )

class Account(models.Model):
    acc_number = models.IntegerField(default=get_acc_num)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return "{}: {}".format(self.acc_number, self.balance)
    
# Instead of reciever lets just keep the Account of the reciever
class Transaction(models.Model):
    amount = models.FloatField(default=0.0)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    #receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    #signator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="signator", default=None)
    recipientAccount = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account")
    timestamp = models.DateTimeField(auto_now_add=True)
    isValidated = models.BooleanField(default=False)
    
    @classmethod
    def create(self, amount, sender, recipientAccount, isValidated):
        transaction = self(amount=amount, sender=sender, recipientAccount=recipientAccount, isValidated=isValidated)
        return transaction
        

    def __str__(self):
        
        return "Transaction: " + str(self.timestamp)#+ self.sender.name + " -> " + self.receiver.name + ": " + str(self.amount) + " INR"

class ProfileModificationReq(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(default="NONE", max_length=100)
    phone_number = models.CharField(default="NONE", max_length=15, blank=True)

# 192.168.65.164:8000
# 192.168.59.27:8000
