
from django.db import models
from django.contrib.auth.models import User
import uuid

class CustomerProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'MALE'),
        ('Female', 'FEMALE'),
        ('Others', 'OTHERS'),
    ]

    ACCOUNT_TYPE = [
        ('savings', 'SAVINGS'),
        ('current', 'CURRENT'),
        ('bussiness', 'BUSSINESS'),
    ]

    ID_TYPE = [
        ('adhar_card', 'ADHAR_CARD'),
        ('driver', 'DRIVER LICENECE'),
        ('passport', 'PASSPORT'),
    ]

    EMPLOYMENT_STATUS = [
        ('employed', 'EMPLOYED'),
        ('unemployed', 'UNEMPLOYED'),
        ('retired', 'RETIRED'),
        ('student', 'STUDENT'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE)
   
    account_number = models.CharField(max_length=12, unique=True, blank=True)
    id_type = models.CharField(max_length=50, choices=ID_TYPE)
    id_num = models.CharField(max_length=15, null=True)
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)  
    is_active = models.BooleanField(default=False)

    def generate_account_number(self):
        uuid_num = str(uuid.uuid4().int)[:12]
        return uuid_num


    def __str__(self):
        return self.user.username