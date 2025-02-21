
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
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
   
    account_number = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
      
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



class DepositTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='deposit_user')  
    account_number = models.CharField(max_length=20)  
    ifsc_code = models.CharField(max_length=11)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)  
    currency = models.CharField(max_length=3, default='INR')
    order_id = models.CharField(max_length=500,null=True, unique=True) 
    payment_id = models.CharField(max_length=100, blank=True, null=True)  
    signature = models.CharField(max_length=255, blank=True, null=True) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  
    
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.user.username
    

    
class TransferHistory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    TRANSFER_MODES = [
        ('UPI', 'UPI'),
        ('NEFT', 'NEFT'),
        ('RTGS', 'RTGS'),
        ('IMPS', 'IMPS'),
        ('WIRE', 'Wire Transfer'),
    ]

    
    sender = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    receiver_account = models.CharField(max_length=20)  
    receiver_name = models.CharField(max_length=100)  
    receiver_bank_name = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)  

   
    amount = models.DecimalField(max_digits=10, decimal_places=2)  
    currency = models.CharField(max_length=3, default='INR')  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  
    transfer_mode = models.CharField(max_length=10, choices=TRANSFER_MODES, default='UPI')  

   
    order_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  
    payment_id = models.CharField(max_length=100, blank=True, null=True)  
    signature = models.CharField(max_length=255, blank=True, null=True)  

    otp_verification = models.BooleanField(default=False)  # OTP verification status
    remarks = models.TextField(blank=True, null=True)  

   
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.receiver_name






class Kseb_Billpay(models.Model):

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    PAYMENT_MODES = [
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking'),
        ('Debit Card', 'Debit Card'),
        ('Credit Card', 'Credit Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consumer_number = models.CharField(max_length=15)  # Changed to CharField
    bill_number = models.CharField(max_length=20)  # Changed to CharField
    bill_amt = models.DecimalField(max_digits=10, decimal_places=2)  # Changed to DecimalField
    due_date = models.DateField(blank=True, null=True)
    payment_date = models.DateField(auto_now=True)
    transaction_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4,null=True,blank=True)  # Generates unique ID
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default="Pending")
    signature = models.CharField(max_length=255, blank=True, null=True) 
    mode_of_payment = models.CharField(max_length=20, choices=PAYMENT_MODES, blank=True, null=True)
    account_number = models.BigIntegerField(blank=True, null=True)
    bank_name = models.CharField(max_length=50,blank=True, null=True)

    def __str__(self):
        return self.user.username


class WaterBillPayment(models.Model):
  

    PAYMENT_MODES = [
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking'),
        ('Debit Card', 'Debit Card'),
        ('Credit Card', 'Credit Card'),
       
    ]

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    consumer_number = models.CharField(max_length=20, unique=True,null=True)  
    bill_number = models.CharField(max_length=30, unique=True)  
    bill_amount = models.IntegerField()  
    due_date = models.DateField(blank=True, null=True)  
    billing_month = models.CharField(max_length=20,blank=True, null=True) 
    payment_date = models.DateTimeField(auto_now_add=True)  
    transaction_id = models.CharField(max_length=50, unique=True)
    signature = models.CharField(max_length=255, blank=True, null=True)  
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)  
    amount_paid = models.IntegerField(null=True, blank=True)  
    mode_of_payment = models.CharField(max_length=20, choices=PAYMENT_MODES) 
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='Pending')  
    

    def __str__(self):
        return self.user.username



class RechargePackage(models.Model):
    SERVICE_PROVIDERS = [
        ('Airtel Digital TV', 'Airtel Digital TV'),
        ('D2H', 'D2H'),
        ('Tata Play', 'Tata Play'),
        ('Dish TV', 'Dish TV'),
    ]

    provider = models.CharField(max_length=50, choices=SERVICE_PROVIDERS)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.provider


class DTHBillPayment(models.Model):
    SERVICE_PROVIDERS = [
        ('Airtel Digital TV', 'Airtel Digital TV'),
        ('D2H', 'D2H'),
        ('Tata Play', 'Tata Play'),
        ('Dish TV', 'Dish TV'),
    ]

    PAYMENT_METHODS = [
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking'),
        
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscriber_id = models.CharField(max_length=11)
    provider = models.CharField(max_length=50, choices=SERVICE_PROVIDERS)
    package = models.ForeignKey(RechargePackage, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.provider} - ₹{self.amount} - {self.payment_status}"



# class DishPayment(models.Model):
#     PAYMENT_STATUS_CHOICES = [
#         ('Pending', 'Pending'),
#         ('Completed', 'Completed'),
#         ('Failed', 'Failed'),
#     ]

#     PAYMENT_MODE_CHOICES = [
#         ('Net Banking', 'Net Banking'),
#         ('UPI', 'UPI'),
#         ('Credit Card', 'Credit Card'),
#         ('Debit Card', 'Debit Card'),
       
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     consumer_number = models.CharField(max_length=20, unique=True)  
#     bill_number = models.CharField(max_length=30, unique=True)  
#     bill_amount = models.IntegerField() 
#     amount_paid = models.IntegerField()
#     payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
#     payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, null=True, blank=True)
#     transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
#     bank_name = models.CharField(max_length=100, null=True, blank=True)
#     bank_transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
#     payment_time = models.DateTimeField(auto_now_add=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.user.username
    
    
