from django.db import models
from django.contrib.auth.models import User


class Wallet(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    private_key = models.TextField()

    def __str__(self):
        return self.owner.username


class Transaction(models.Model):
    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sent')
    receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='received')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)
