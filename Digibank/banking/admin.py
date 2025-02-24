from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomerProfile)
admin.site.register(DepositTransaction)
admin.site.register(TransferHistory)

admin.site.register(Kseb_Billpay)
admin.site.register(RechargePackage)
admin.site.register(DTHBillPayment)
admin.site.register(WaterBillPayment)
admin.site.register(Loanmanagement)
admin.site.register(CardRequest)

