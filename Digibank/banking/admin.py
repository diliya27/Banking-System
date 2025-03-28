from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(DepositTransaction)
admin.site.register(TransferHistory)

admin.site.register(Kseb_Billpay)
admin.site.register(RechargePackage)
admin.site.register(DTHBillPayment)
admin.site.register(WaterBillPayment)
admin.site.register(Loanmanagement)
admin.site.register(CardRequest)
from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'is_blocked')  # Show block status
    list_filter = ('is_blocked',)
    actions = ['block_users', 'unblock_users']  # Add admin actions

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)
        self.message_user(request, "Selected users have been blocked.")

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
        self.message_user(request, "Selected users have been unblocked.")

    block_users.short_description = "Block selected users"
    unblock_users.short_description = "Unblock selected users"


