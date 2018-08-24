from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


class Profile(models.Model):
    balance = models.FloatField(default=0.0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return "User: " + self.user.name
    
class Transaction(models.Model):
    amount = models.FloatField(default=0.0)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    signator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="signator")
    timestamp = models.DateTimeField(auto_now_add=True)
    isCritical = models.BooleanField(default=False)


    def __str__(self):
        return "Transaction: " + self.sender.name + " -> " + self.receiver.name + ": " + str(self.amount) + " INR"