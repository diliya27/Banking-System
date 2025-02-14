from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from smtplib import SMTPException
import uuid
from .models import CustomerProfile
from django.contrib.auth import authenticate, login
from .models import  DepositTransaction,TransferHistory,Kseb_Billpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import razorpay

from django.db.models import Sum

from django.contrib.auth.decorators import login_required



 

def index(request):
    return render(request, "index.html")


def generate_unique_account_number():
    """Generate a 12-digit unique account number."""
    while True:
        account_number = str(uuid.uuid4().int)[:12]
        if not CustomerProfile.objects.filter(account_number=account_number).exists():
            return account_number


def send_account_number_email(customer_email, account_number):
    
    subject = "Your New Account Number"
    message = f"""Dear Customer,

Your account has been successfully created.
Your account number is: {account_number} IFSC CODE:FDRL0001033

Thank you for choosing us!
"""
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [customer_email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        print(f"Email successfully sent to {customer_email}")
    except SMTPException as e:
        print(f"Error sending email to {customer_email}: {e}")


def create_account_view(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip_code")
        email = request.POST.get("email")
        account_type = request.POST.get("account_type")
        id_type = request.POST.get("id_type")
        id_num = request.POST.get("id_num")
        employment_status = request.POST.get("employment_status")

        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "create_account.html", {"data": request.POST})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "create_account.html", {"data": request.POST})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "create_account.html", {"data": request.POST})

        try:
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,  
            )

            # Generate unique account number
            account_number = generate_unique_account_number()

           
            profile = CustomerProfile.objects.create(
                user=user,
                dob=dob,
                gender=gender,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                account_type=account_type,
                account_number=account_number,
                id_type=id_type,
                id_num=id_num,
                employment_status=employment_status,
            )

            # Send account number via email
            send_account_number_email(email, account_number)

            messages.success(
                request,
                f"Account created successfully. Your account number is: {profile.account_number}",
            )
            return redirect("index")

        except IntegrityError as e:
            messages.error(request, f"Database error: {e}")
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")

    return render(request, "create_account.html")

def login_view(request):
    if request.method == "POST":
        account_number = request.POST.get("account_number")
        password = request.POST.get("password")

        try:
            # Retrieve the user using the account number
            customer = CustomerProfile.objects.get(account_number=account_number)
            user = customer.user  # Get the associated user
            authenticated_user = authenticate(request, username=user.username, password=password)

            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, "Login successful!")
                return redirect("user_dashboard")  
            else:
                messages.error(request, "Invalid password. Please try again.")

        except CustomerProfile.DoesNotExist:
            messages.error(request, "Account number not found. Please check your details.")

    return render(request, "login.html")

def user_dashboard_view(request):
    return render(request,"user_dashboard.html")
 

def accounts_page(request):
    user = request.user
    deposit_total = DepositTransaction.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] 
    transfer_total = TransferHistory.objects.filter(sender=user).aggregate(Sum('amount'))['amount__sum'] 
    total = deposit_total - transfer_total  
    customer_profile = CustomerProfile.objects.get(user=user)
    context = {
        "user": user,
        "account": DepositTransaction.objects.filter(user=user),
        "customer_profile": customer_profile,
        "total": total,
    }

    return render(request, "accounts.html", context)



    
def transfer_view(request):
    return render(request,'transfers.html')



def deposit_create_view(request):
    if request.method == "POST":
        user = request.user
        amount = request.POST.get("amount")
        ifsc_code = request.POST.get("ifsc_code")
        account_number = request.POST.get("account_number")

        try:
            amount = float(amount)
            if amount <= 0:
                return HttpResponse("Invalid deposit amount")
        except ValueError:
            return HttpResponse("Invalid amount format")
 # Create the deposit transaction 
        deposit = DepositTransaction.objects.create(
            user=user,
            account_number=account_number,
            ifsc_code=ifsc_code,
            amount=amount,
            status="pending"
        )
        deposit.save()

        # Now redirect to the Razorpay order creation view
        return redirect("create_razorpay_order", deposit_id=deposit.id)

    return render(request, "deposit.html") 



def create_razorpay_order_view(request, deposit_id):
    try:
        deposit = DepositTransaction.objects.get(id=deposit_id)
    except Exception as e:
        print(e,'===================')    

    if deposit.status != "pending":
        return HttpResponse("Invalid deposit status.")

    # Initialize Razorpay client
    client = razorpay.Client(auth=('rzp_test_mwbtpQAgt0Xjve', 'T6oVFCs7TUaMahVVkE0JHes9'))
    razorpay_order = client.order.create(
        {"amount": int(deposit.amount * 100), "currency": "INR", "payment_capture": "1"}
    )

    # Update the deposit with the Razorpay order ID
    deposit.order_id = razorpay_order["id"]
    deposit.save()

    # Pass the deposit and Razorpay order details to the template
  
    return render(
        request,
        "deposit.html",
        {
            "deposit": deposit,
            "razorpay_order_id":deposit.order_id,
            "razorpay_signature":deposit.signature,
            "razorpay_key": 'rzp_test_mwbtpQAgt0Xjve',
            "callback_url": "http://127.0.0.1:8000/razorpay/callback/",
        }
    )
    



# This view will handle the callback from Razorpay after the payment
@csrf_exempt 
def razorpay_callback(request):
    if request.method == "POST":
        # Parse the POST data from Razorpay
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")
        print(razorpay_payment_id)
        print(razorpay_order_id)
        print(razorpay_signature)

        try:
            # Get the deposit transaction
            deposit = DepositTransaction.objects.get(order_id=razorpay_order_id)
            print(deposit)

            # Initialize Razorpay client to verify the payment signature
            client = razorpay.Client(auth=('rzp_test_mwbtpQAgt0Xjve', 'T6oVFCs7TUaMahVVkE0JHes9'))  

            # Check the payment signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }

            client.utility.verify_payment_signature(params_dict)  # Verify the payment signature
            
            # If the signature is valid, update the deposit status to "successful"
            deposit.status = "successful"
            deposit.save()

            return redirect("transfers")

        except razorpay.errors.SignatureVerificationError:
            # If the signature verification fails, update the deposit status to "failed"
            deposit.status = "failed"
            deposit.save()
            return HttpResponse("Payment verification failed")

    return HttpResponse("Invalid request method")



def account_transfer_view(request):
    if request.method == "POST":
        receiver_bank_name = request.POST.get("receiver_bank_name")
        receiver_account = request.POST.get("receiver_account")
        receiver_name = request.POST.get("receiver_name")
        ifsc_code = request.POST.get("ifsc_code")
        amount = request.POST.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                return HttpResponse("Invalid Transfer Amount")
        except ValueError:
            return HttpResponse("Invalid amount format")

        amount_in_paise = int(amount * 100)  

       
        # Save transfer history
        transfer = TransferHistory.objects.create(
            sender=request.user,
            receiver_bank_name=receiver_bank_name,
            receiver_account=receiver_account,
            receiver_name=receiver_name,
            ifsc_code=ifsc_code,
            amount=amount_in_paise,
            status="pending"
        )

        return redirect("transfer_razorpay_order", transfer_id=transfer.id)

    return render(request, "account_transfer.html")


def transfer_razorpay_order_view(request, transfer_id):
    transfer = TransferHistory.objects.get(id=transfer_id)

    if transfer.status != "pending":
        return HttpResponse("Invalid transfer status.")

    client = razorpay.Client(auth=('rzp_test_mwbtpQAgt0Xjve', 'T6oVFCs7TUaMahVVkE0JHes9'))

    amt = int(transfer.amount)
    razorpay_order = client.order.create({"amount":amt,"currency": "INR","payment_capture": "1"})

    transfer.order_id = razorpay_order["id"]
    transfer.save()

    return render(request, "account_transfer.html", {
        "transfer": transfer,
        "razorpay_key": 'rzp_test_mwbtpQAgt0Xjve',
        "callback_url": "http://127.0.0.1:8000/razorpay/callback/tranfer/",
    })


@csrf_exempt 
def razorpay_transfer_callback(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        

        try:

            transfer = TransferHistory.objects.get(order_id=razorpay_order_id)
            client = razorpay.Client(auth=('rzp_test_mwbtpQAgt0Xjve', 'T6oVFCs7TUaMahVVkE0JHes9'))

            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }

            client.utility.verify_payment_signature(params_dict)

            # Mark transfer as successful
            transfer.status = "successful"
            transfer.save()

            return redirect("transfers")

        except razorpay.errors.SignatureVerificationError:
            transfer.status = "failed"
            transfer.save()
            return HttpResponse("Payment verification failed")

    return HttpResponse("Invalid request method")




@login_required
  
def view_statement(request):
    user = request.user
    
    # Fetch deposit and transfer history
    deposit_view = DepositTransaction.objects.filter(user=user).order_by('-created_at')
    transfer_view = TransferHistory.objects.filter(sender=user).order_by('-created_at')

    # Add a transaction type for better differentiation
    deposit_list = [{"type": "Credit", "amount": d.amount, "created_at": d.created_at,"status":d.status} for d in deposit_view]
    transfer_list = [{"type": "Debit", "amount": t.amount, "created_at": t.created_at,"status":t.status} for t in transfer_view]

    # Merge both lists
    transaction_history = sorted(deposit_list + transfer_list, key=lambda x: x["created_at"], reverse=True)

    # Calculate total credits and debits
    total_credits = sum(d["amount"] for d in deposit_list)
    total_debits = sum(t["amount"] for t in transfer_list)
    balance = total_credits - total_debits

    context = {
        "user": user,
        "transaction_history": transaction_history,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "balance": balance
    }

    return render(request, 'view_statement.html', context)

def billpay(request):
    return render(request,'billpay.html')

def kseb_pay_view(request):
    # if request.method == "POST":
    #     consumer_number=request.POST.get("consumer_number")
    #     bill_number=request.POST.get("bill_number")
    #     bill_amt=request.POST.get("bill_amt")

    #     try:
    #         bill_amt = float(bill_amt)
    #         if bill_amt <= 0:
    #             return HttpResponse("Invalid Transfer Amount")
    #     except ValueError:
    #         return HttpResponse("Invalid amount format")
    #     amount_in_paise = int(bill_amt * 100)

    #     kseb_pay=Kseb_Billpay.objects.create(
    #         user=request.user,
    #         consumer_number=consumer_number,
    #         bill_number=bill_number,
    #         bill_amt=amount_in_paise

    #     )

    #     return redirect('billpay_razorpay',kseb_id=kseb_pay.id)
    return render(request,"kseb_billpay.html")



# def kseb_razorpay_view(request, kseb_id):
#     kseb = Kseb_Billpay.objects.get(id=kseb_id)

#     if kseb.status != "pending":
#         return HttpResponse("Invalid kseb status.")

#     client = razorpay.Client(auth=('rzp_test_mwbtpQAgt0Xjve', 'T6oVFCs7TUaMahVVkE0JHes9'))

#     amt = int(kseb.amount)
#     razorpay_order = client.order.create({"amount":amt,"currency": "INR","payment_capture": "1"})

#     kseb.order_id = razorpay_order["id"]
#     kseb.save()

#     return render(request, "account_kseb.html", {
#         "kseb": kseb,
#         "razorpay_key": 'rzp_test_mwbtpQAgt0Xjve',
#         "callback_url": "http://127.0.0.1:8000/razorpay/callback/tranfer/",
#     })

# @csrf_exempt 
# def razorpay_kseb_callback(request):
#     if request.method == "POST":
#         razorpay_payment_id = request.POST.get("razorpay_payment_id")
#         razorpay_order_id = request.POST.get("razorpay_order_id")
#         razorpay_signature = request.POST.get("razorpay_signature")

        

#         try:

#             kseb = Kseb_Billpay.objects.get(order_id=razorpay_order_id)
#             client = razorpay.Client(auth=('rzp_test_mwbtpQAgt0Xjve', 'T6oVFCs7TUaMahVVkE0JHes9'))

#             params_dict = {
#                 "razorpay_order_id": razorpay_order_id,
#                 "razorpay_payment_id": razorpay_payment_id,
#                 "razorpay_signature": razorpay_signature,
#             }

#             client.utility.verify_payment_signature(params_dict)

#             # Mark transfer as successful
#             kseb.status = "successful"
#             kseb.save()

#             return redirect("transfers")

#         except razorpay.errors.SignatureVerificationError:
#             kseb.status = "failed"
#             kseb.save()
#             return HttpResponse("Payment verification failed")

#     return HttpResponse("Invalid request method")



        





    
def dish_billpay_view(request):
    return render(request,'dish_billpay.html')
def water_billpay_view(request):
    return render(request,'water_billpay.html')
    




    






      
      



