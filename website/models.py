from django.db import models
from django.contrib.auth.models import User

def getIFSCCode():
    # TODO generate codes
    return "randomString"

def getAccNum():
    # TODO generate number
    return 'Sexy thing'

# A single person can have multiple bank accounts though. They can be in the same bank or some external bank :/
# To access the multiple bank detials for a Profile p, just do p.account_set.objects.all() [Need to test this once]
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    address = models.TextField(default="NONE", max_length=100)
    phone_number = models.CharField(max_length=15, blank=True) # validators should be a list

    # Info for KYC
    # Assign common permissions for all types of users

class Employee(Profile):
    pass

class Customer(Profile):
    pass

class Account(models.Model):
    ifsccode = models.CharField(default=getIFSCCode, max_length=50)
    accNumber = models.CharField(default=getAccNum, max_length=50)
    BankName = models.CharField(default="NULL", max_length=50)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return "Account Deatails ifsccode: {}, accNumber: {}, BankName: {}".format(self.ifsccode, self.accNumber, self.BankName)
    
# Instead of reciever lets just keep the Account of the reciever
class Transaction(models.Model):
    amount = models.FloatField(default=0.0)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    #receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    signator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="signator", default=None)
    recipientAccount = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account")
    timestamp = models.DateTimeField(auto_now_add=True)
    isCritical = models.BooleanField(default=False)
    isValidated = models.BooleanField(default=False)
    
    @classmethod
    def create(self, amount, sender, recipientAccount, isCritical):
        transaction = self(amount=amount, sender=sender, recipientAccount=recipientAccount, isCritical=isCritical)
        # store in DB or whatever, will use a queue of pending transactions
        return transaction
        

    def __str__(self):
        return "Transaction: " + self.sender.name + " -> " + self.receiver.name + ": " + str(self.amount) + " INR"


        



# I will also keep the server running in another terminal just in case you guys need to test some shit, cool?
# 192.168.65.73:8002


# I will also keep the server running in another terminal just in case you guys need to test some shit, cool?
# 192.168.65.73:8002