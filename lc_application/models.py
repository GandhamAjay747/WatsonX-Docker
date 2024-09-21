from django.db import models

# Create your models here.

class Registration(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=128)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
    


class LetterOfCredit(models.Model):
    lc_number = models.CharField(max_length=100)
    applicant_name = models.CharField(max_length=255)
    beneficiary_name = models.CharField(max_length=255)
    issuing_bank = models.CharField(max_length=255)
    advising_bank = models.CharField(max_length=255)
    negotiating_bank = models.CharField(max_length=255)
    confirming_bank = models.CharField(max_length=255)
    lc_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.lc_number