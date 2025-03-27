from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError
from smtplib import SMTPException
import uuid
from .models import CustomerProfile
from django.contrib.auth import authenticate, login
from .models import  DepositTransaction,TransferHistory,Kseb_Billpay,WaterBillPayment,DTHBillPayment, RechargePackage,Loanmanagement,CardRequest, BillHistory
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.db.models import Sum
from django.conf import settings
from django.contrib.auth.decorators import login_required

import razorpay

from django.http import HttpResponse,JsonResponse
from reportlab.pdfgen import canvas

from django.urls import reverse

from .models import Kseb_Billpay




from django.utils.timezone import make_aware
from django.core.paginator import Paginator
from datetime import datetime
from django.contrib.auth import logout

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

import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from .models import CustomerProfile


def create_account_view(request):
    if request.method == "POST":
        # Retrieve form data
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

        # Validate passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "create_account.html", {"data": request.POST})

        # Check for existing username and email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "create_account.html", {"data": request.POST})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "create_account.html", {"data": request.POST})

        # Validate ID number based on ID type
        if id_type == 'adhar_card':
            if not re.fullmatch(r'\d{12}', id_num):
                messages.error(request, "Invalid Aadhaar number. It must be exactly 12 digits.")
                return render(request, "create_account.html", {"data": request.POST})
        elif id_type == 'pan_card':
            if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', id_num):
                messages.error(request, "Invalid PAN number. It must be exactly 10 characters in the format ABCDE1234F.")
                return render(request, "create_account.html", {"data": request.POST})
        else:
            messages.error(request, "Invalid ID type selected.")
            return render(request, "create_account.html", {"data": request.POST})

        # Attempt to create user and profile within a transaction
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                )

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

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from .models import BillHistory, DepositTransaction, TransferHistory, CustomerProfile

def user_dashboard_view(request):
    user = request.user

    # Fetch Bill History and sum bill_amount (default to 0 if None)
    Bill_history = BillHistory.objects.filter(user=user)
    bill_debited = Bill_history.aggregate(Sum('bill_amount'))['bill_amount__sum'] or 0

    # Fetch Deposit Transactions (only successful ones)
    deposit_total = DepositTransaction.objects.filter(user=user, status="successful").aggregate(Sum('amount'))['amount__sum'] or 0

    # Fetch Transfer History and sum amounts (only successful ones)
    transfer_total = TransferHistory.objects.filter(sender=user, status="successful").aggregate(Sum('amount'))['amount__sum'] or 0

    # Ensure transfer_total is not None before adding bill_debited
    transfer_total += bill_debited  # No NoneType issue here

    # Calculate total balance
    total = deposit_total - transfer_total  

    # Fetch Customer Profile
    customer_profile = get_object_or_404(CustomerProfile, user=user)

    # Fetch Bill History sorted by date
    bill_history = BillHistory.objects.filter(user=user).order_by('-created_at')

    # Prepare context for template rendering
    context = {
        "user": user,
        "account": DepositTransaction.objects.filter(user=user, status="successful"),
        "customer_profile": customer_profile,
        "total": total,
        "bill_history": bill_history
    }

    return render(request, "user_dashboard.html", context)

def accounts_page(request):
    user = request.user
    Bill_history = BillHistory.objects.filter(user=user)
    bill_debited = Bill_history.aggregate(Sum('bill_amount'))['bill_amount__sum'] or 0

    # Corrected status values
    deposit_total = DepositTransaction.objects.filter(user=user, status="successful").aggregate(Sum('amount'))['amount__sum'] or 0
    transfer_total = TransferHistory.objects.filter(sender=user, status="successful").aggregate(Sum('amount'))['amount__sum'] +bill_debited or 0
    total = deposit_total - transfer_total  
    # print(deposit_total)
    # print(transfer_total)
    # print(total)
    # Handle case where CustomerProfile does not exist
    customer_profile = get_object_or_404(CustomerProfile, user=user)

    context = {
        "user": user,
        "account": DepositTransaction.objects.filter(user=user, status="success"),
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
   
    deposit = DepositTransaction.objects.get(id=deposit_id)
       

    if deposit.status != "pending":
        return HttpResponse("Invalid deposit status.")

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
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
                
                "callback_url": "http://127.0.0.1:8000/razorpay/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                
            },
        )

    



# This view will handle the callback from Razorpay after the payment

@csrf_exempt
def razorpay_callback(request):
    if request.method == "POST":
        try:
        # Parse the POST data from Razorpay
            razorpay_payment_id = request.POST.get("razorpay_payment_id")
            razorpay_order_id = request.POST.get("razorpay_order_id")
            razorpay_signature = request.POST.get("razorpay_signature")
           
        
            # Get the deposit transaction
            deposit = DepositTransaction.objects.get(order_id=razorpay_order_id)
            print(deposit)

            # Initialize Razorpay client to verify the payment signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
             # Check the payment signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
            try:

                client.utility.verify_payment_signature(params_dict)  # Verify the payment signature
                
                # If the signature is valid, update the deposit status to "successful"
                deposit.status = "successful"
                deposit.payment_id = razorpay_payment_id
                deposit.signature = razorpay_signature
                deposit.save()
                

                return redirect("transfers")

            except razorpay.errors.SignatureVerificationError:
                # If the signature verification fails, update the deposit status to "failed"
                deposit.status = "failed"
                deposit.save()
                return HttpResponse("Payment verification failed")
        except DepositTransaction.DoesNotExist:
            return JsonResponse({"error": "Order not found"})
        except Exception as e:
            return JsonResponse({"error": "Something went wrong"})


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
# Save transfer history
        transfer = TransferHistory.objects.create(
            sender=request.user,
            receiver_bank_name=receiver_bank_name,
            receiver_account=receiver_account,
            receiver_name=receiver_name,
            ifsc_code=ifsc_code,
            amount=amount,
            status="pending"
        )
        transfer.save()

        return redirect("transfer_razorpay_order", transfer_id=transfer.id)

    return render(request, "account_transfer.html")


def transfer_razorpay_order_view(request, transfer_id):
    transfer = TransferHistory.objects.get(id=transfer_id)

    if transfer.status != "pending":
        return HttpResponse("Invalid transfer status.")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    razorpay_order = client.order.create({"amount":int(transfer.amount * 100),"currency": "INR","payment_capture": "1"})

    transfer.order_id = razorpay_order["id"]
    transfer.save()

    return render(request, "account_transfer.html", {
        "transfer": transfer,
         "razorpay_order_id":transfer.order_id,
        "razorpay_key":  settings.RAZORPAY_KEY_ID,
        "callback_url": "http://127.0.0.1:8000/razorpay/callback/tranfer/",
    })


@csrf_exempt 
def razorpay_transfer_callback(request):
    if request.method == "POST":
        try:
            razorpay_payment_id = request.POST.get("razorpay_payment_id")
            razorpay_order_id = request.POST.get("razorpay_order_id")
            razorpay_signature = request.POST.get("razorpay_signature")

            transfer = TransferHistory.objects.get(order_id=razorpay_order_id)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
            try:
                client.utility.verify_payment_signature(params_dict)
                

                # Mark transfer as successful
                transfer.status = "successful"
                transfer.payment_id = razorpay_payment_id
                transfer.signature = razorpay_signature
                transfer.save()

                return redirect("transfers")

            except razorpay.errors.SignatureVerificationError:
                transfer.status = "failed"
                transfer.save()
                return HttpResponse("Payment verification failed")
        except TransferHistory.DoesNotExist:
            return JsonResponse({"error": "Order not found"})
        except Exception as e:
            return JsonResponse({"error": "Something went wrong"})                                                                                                 

    return HttpResponse("Invalid request method")







@login_required
def view_statement(request):
    user = request.user

    # Fetch deposit and transfer history (only successful transactions)
    deposit_view = DepositTransaction.objects.filter(user=user,status="successful").order_by('-created_at')
    transfer_view = TransferHistory.objects.filter(sender=user,status="successful").order_by('-created_at')
    kseb_view=Kseb_Billpay.objects.filter(user=user,payment_status="success")
    water_view=WaterBillPayment.objects.filter(user=user,payment_status="success")
    dth_view=DTHBillPayment.objects.filter(user=user,payment_status="success")
    
    id = user.id
    print(id)
    data = CustomerProfile.objects.get(user_id=id)
    acc_num = data.account_number

    # Add a transaction type for better differentiation
    deposit_list = [
        {"type": "Credit", "amount": d.amount, "created_at": d.created_at, "status": d.status}
        for d in deposit_view
    ]
    transfer_list = [
        {"type": "Debit", "amount": t.amount, "created_at": t.created_at, "status": t.status}
        for t in transfer_view
    ]
    kseb_list=[
        {"type":"Debit","amount":b.bill_amt,"created_at":b.created_at,"status":b.payment_status}
        for b in kseb_view
    ]
    water_list=[
        {"type":"Debit","amount":w.bill_amount,"created_at":w.created_at,"status":w.payment_status}
        for w in water_view
    ]
    dth_list=[
        {"type":"Debit","amount":db.amount,"created_at":db.created_at,"status":db.payment_status}
        for db in dth_view
    ]

    # Merge both lists
    transaction_history = sorted(deposit_list + transfer_list+kseb_list+water_list+dth_list, key=lambda x: x["created_at"], reverse=True)

    # Calculate total credits and debits (only successful transactions)
    total_credits = sum(d["amount"] for d in deposit_list)
    total_debits = sum(t["amount"] for t in transfer_list)+sum(k["amount"]for k in kseb_list)+sum(w["amount"]for w in water_list)+sum(db["amount"]for db in dth_list)
    balance = total_credits - total_debits

    context = {
        "user": user,
        "transaction_history": transaction_history,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "balance": balance,
        "acc_num": acc_num
    }

    return render(request, 'view_statement.html', context)

  



@login_required
def download_statement_pdf(request):
    user = request.user
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user = request.user
    id=user.id 
    data=CustomerProfile.objects.get(user_id=id)
    acc_num=data.account_number

    # Convert date strings to datetime objects
    if start_date:
        start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))

    # Fetch filtered transactions
    deposit_view = DepositTransaction.objects.filter(user=user)
    transfer_view = TransferHistory.objects.filter(sender=user)

    if start_date and end_date:
        deposit_view = deposit_view.filter(created_at__range=[start_date, end_date])
        transfer_view = transfer_view.filter(created_at__range=[start_date, end_date])

    deposit_list = [{"Type": "Credit", "Amount": d.amount, "Created At": d.created_at, "Status": d.status} for d in deposit_view]
    transfer_list = [{"Type": "Debit", "Amount": t.amount, "Created At": t.created_at, "Status": t.status} for t in transfer_view]

    transaction_history = sorted(deposit_list + transfer_list, key=lambda x: x["Created At"], reverse=True)

    # Create PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="transaction_statement.pdf"'

    pdf = canvas.Canvas(response)
    pdf.setTitle("Transaction Statement")

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 770, "Transaction Statement")

    # User Info
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 740, f"User: {user.username}")
    pdf.drawString(50, 720, f"User: {acc_num}")
    pdf.drawString(50, 700, f"Date Range: {start_date.date() if start_date else 'N/A'} - {end_date.date() if end_date else 'N/A'}")

    # Table Headers
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, 670, "Date & Time")
    pdf.drawString(200, 670, "Type")
    pdf.drawString(300, 670, "Amount")
    pdf.drawString(400, 670, "Status")

    pdf.line(50, 665, 500, 665)  # Draw a line under headers

    # Add transaction details
    y_position = 650
    pdf.setFont("Helvetica", 10)
    for transaction in transaction_history:
        pdf.drawString(50, y_position, str(transaction["Created At"].strftime("%Y-%m-%d %H:%M:%S")))
        pdf.drawString(200, y_position, transaction["Type"])
        pdf.drawString(300, y_position, f"₹{transaction['Amount']}")
        pdf.drawString(400, y_position, transaction["Status"])
        y_position -= 20  # Move to the next row

        # Add a new page if space runs out
        if y_position < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = 750

    pdf.save()
    return response  




@login_required
def transaction_history(request):
    user = request.user
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Convert date strings to datetime objects
    if start_date:
        start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))

    # Fetch filtered transactions
    deposit_view = DepositTransaction.objects.filter(user=user)
    transfer_view = TransferHistory.objects.filter(sender=user)
    

    if start_date and end_date:
        deposit_view = deposit_view.filter(created_at__range=[start_date, end_date])
        transfer_view = transfer_view.filter(created_at__range=[start_date, end_date])
        
    deposit_list = [{"Type": "Credit", "Amount": d.amount, "Created At": d.created_at, "Status": d.status} for d in deposit_view]
    transfer_list = [{"Type": "Debit", "Amount": t.amount, "Created At": t.created_at, "Status": t.status} for t in transfer_view]
    
    transaction_history = sorted(deposit_list + transfer_list, key=lambda x: x["Created At"], reverse=True)

    # **Paginate results (10 transactions per page)**
    paginator = Paginator(transaction_history, 10)  # 10 transactions per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "transaction_history.html", {"page_obj": page_obj, "start_date": start_date, "end_date": end_date})





def billpay(request):
    return render(request, 'billpay.html')


def kseb_pay_view(request):
   
    if request.method == "POST":
        user=request.user
        consumer_number = request.POST.get("consumer_number")
        bill_number = request.POST.get("bill_number")
        bill_amt = request.POST.get("bill_amt")


        try:
            bill_amt = float(bill_amt)
            if bill_amt <= 0:
                return HttpResponse("Invalid bill Amount")
        except ValueError:
            return HttpResponse("Invalid amount format")
         # Ensure user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized")
        
        if Kseb_Billpay.objects.filter(bill_number=bill_number).exists():
            return HttpResponse("This bill number has already been used for payment.")


        

        kseb_pay = Kseb_Billpay.objects.create(
            user=user,
            consumer_number=consumer_number,
            bill_number=bill_number,
            bill_amt=bill_amt,
            payment_status="pending"
        )
        kseb_pay.save()
        print(kseb_pay)

        return redirect('billpay_razorpay', kseb_pay_id=kseb_pay.id)

    return render(request, "kseb_billpay_base.html")


def kseb_razorpay_view(request, kseb_pay_id):
    try:
        kseb_pay = Kseb_Billpay.objects.get(id=kseb_pay_id)
    except Kseb_Billpay.DoesNotExist:
        return HttpResponse("Payment record not found")
    

    if kseb_pay.payment_status != "pending":
        return HttpResponse("Invalid KSEB status.")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
            razorpay_order = client.order.create({
                "amount": int(kseb_pay.bill_amt * 100), 
                "currency": "INR", 
                "payment_capture": "1"
            })
            kseb_pay.transaction_id = razorpay_order["id"]
            kseb_pay.save()
            print(razorpay_order)
    except Exception as e:
        return HttpResponse(f"Error creating Razorpay order: {str(e)}")     

    return render(request, "kseb_billpay_base.html", {
            "kseb_pay": kseb_pay,
            "razorpay_order_id":kseb_pay.transaction_id,
            "razorpay_key":settings.RAZORPAY_KEY_ID,
            "callback_url": "http://127.0.0.1:8000/razorpay/callback/kseb_billpay/",
        })
    
   


@csrf_exempt
def razorpay_kseb_callback(request):
    if request.method != "POST":
        return HttpResponse("Invalid request method")
       
        
        
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")


    print(razorpay_payment_id)
    print(razorpay_order_id)
    print(razorpay_signature)

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return JsonResponse({"error": "Missing payment details"})

    try:    
        kseb_pay = Kseb_Billpay.objects.get(transaction_id=razorpay_order_id)
    except Kseb_Billpay.DoesNotExist:
        return JsonResponse({"error": "Order not found"})

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:

        client.utility.verify_payment_signature(params_dict)

        # Mark transfer as successful
        kseb_pay.payment_status = "success"
        kseb_pay.transaction_id = razorpay_payment_id
        kseb_pay.signature = razorpay_signature

        kseb_pay.save()

        BillHistory.objects.create(user=kseb_pay.user, 
                                   bill_type="KSEB",
                                   transaction_id=razorpay_payment_id, 
                                   bill_amount=kseb_pay.bill_amt, 
                                   payment_status="success")

        
        return redirect("billpay")

    except razorpay.errors.SignatureVerificationError:
        kseb_pay.payment_status = "failed"
        kseb_pay.save()
        return HttpResponse("Payment verification failed")


    except Exception as e:
        return JsonResponse({"error": f"Something went wrong: {str(e)}"}, status=500)




def water_billpay_view(request):
    if request.method == "POST":
        user=request.user
        consumer_number = request.POST.get("consumer_number")
        bill_number = request.POST.get("bill_number")
        bill_amount = request.POST.get("bill_amount")

        try:
            bill_amount = float(bill_amount)
            if bill_amount <= 0:
                return HttpResponse("Invalid bill Amount")
        except ValueError:
            return HttpResponse("Invalid amount format")
         # Ensure user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized")
        
        if WaterBillPayment.objects.filter(bill_number=bill_number).exists():
            return HttpResponse("This bill number has already been used for payment.")
        
        water_billpay = WaterBillPayment.objects.create(
            user=user,
            consumer_number=consumer_number,
            bill_number=bill_number,
            bill_amount=bill_amount,
            payment_status ="pending"
            
        )
        water_billpay.save()
        print(water_billpay)

        return redirect('waterbill_razorpay',water_billpay_id=water_billpay.id)
    return render(request,"water_billpay_base.html")

def water_razorpay_view(request,water_billpay_id):
    try:
        water_billpay=WaterBillPayment.objects.get(id=water_billpay_id)
    except WaterBillPayment.DoesNotExist:
        return HttpResponse("Payment record not found")
    
    print(water_billpay.payment_status)

    if water_billpay.payment_status != "pending":
        return HttpResponse("Invalid water bill status.")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

 
    try:
        razorpay_order = client.order.create({"amount": int(water_billpay.bill_amount * 100)  , "currency": "INR", "payment_capture": "1"})

        water_billpay.transaction_id= razorpay_order["id"]
        water_billpay.save()
        print(razorpay_order)
    except Exception as e:
        return HttpResponse(f"Error creating Razorpay order: {str(e)}") 

    return render(request, "water_billpay_base.html", {
        "water_billpay": water_billpay,
        "razorpay_order_id":water_billpay.transaction_id,
        "razorpay_key":  settings.RAZORPAY_KEY_ID,
        "callback_url": "http://127.0.0.1:8000/razorpay/callback/water_billpay/",
    })


@csrf_exempt
def razorpay_water_callback(request):
    if request.method != "POST":
        return HttpResponse("Invalid request method")

    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")
    print(razorpay_order_id,razorpay_payment_id,razorpay_signature)

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return JsonResponse({"error": "Missing payment details"})


    try:
        water_billpay = WaterBillPayment.objects.get(transaction_id=razorpay_order_id)
    except WaterBillPayment.DoesNotExist:
        return JsonResponse({"error": "Order not found"})   
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }
    try:

        client.utility.verify_payment_signature(params_dict)

        # Mark transfer as successful
        water_billpay.payment_status = "success"
        water_billpay.transaction_id = razorpay_payment_id
        water_billpay.signature = razorpay_signature
        water_billpay.save()
        BillHistory.objects.create(user=water_billpay.user,
                                   bill_type="Water",
                                   transaction_id=razorpay_payment_id,
                                   bill_amount=water_billpay.bill_amount,
                                   payment_status="success")
        return redirect("billpay")

    except razorpay.errors.SignatureVerificationError:
        water_billpay.payment_status = "failed"
        water_billpay.save()
        return HttpResponse("Payment verification failed")
    
    except Exception as e:
        return JsonResponse({"error": "Something went wrong"})


 




@login_required
def dth_bill_payment_view(request):
    
    packages = RechargePackage.objects.all()

    if request.method == "POST":
        user = request.user
        subscriber_id = request.POST.get("subscriber_id")
        provider = request.POST.get("provider")
        package_id = request.POST.get("package_id")
        payment_method = request.POST.get("payment_method")

        try:
            package = RechargePackage.objects.get(id=package_id, provider=provider)
        except RechargePackage.DoesNotExist:
            return HttpResponse("Invalid package selected.")

       
        dth_payment = DTHBillPayment.objects.create(
            user=user,
            subscriber_id=subscriber_id,
            provider=provider,
            package=package,
            amount=package.amount,
            payment_method=payment_method,
            payment_status="pending",
        )

        return redirect('dth_razorpay_payment', dth_payment_id=dth_payment.id)

    return render(request, "dth_bill_payment.html", {"packages": packages})


@login_required
def dth_razorpay_payment_view(request, dth_payment_id):
    
    try:
        dth_payment = DTHBillPayment.objects.get(id=dth_payment_id)
    except DTHBillPayment.DoesNotExist:
        return HttpResponse("Payment record not found.")

    if dth_payment.payment_status != "pending":
        return HttpResponse("Invalid payment status.")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        razorpay_order = client.order.create({
            "amount": int(dth_payment.amount * 100),
            "currency": "INR",
            "payment_capture": "1",
        })

        dth_payment.transaction_id = razorpay_order["id"]
        dth_payment.save()
    except Exception as e:
        return HttpResponse(f"Error creating Razorpay order: {str(e)}")

    return render(request, "dth_payment.html", {
        "dth_payment": dth_payment,
        "razorpay_order_id": dth_payment.transaction_id,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "callback_url": "/razorpay/callback/dth/",
    })




@csrf_exempt
def razorpay_dth_callback(request):
    
    if request.method != "POST":
        return HttpResponse("Invalid request method")

    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return JsonResponse({"error": "Missing payment details"})

    try:
        dth_payment = DTHBillPayment.objects.get(transaction_id=razorpay_order_id)
    except DTHBillPayment.DoesNotExist:
        return JsonResponse({"error": "Order not found"})

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:
        client.utility.verify_payment_signature(params_dict)

        # Mark payment as successful
        dth_payment.payment_status = "success"
        dth_payment.transaction_id = razorpay_payment_id
        dth_payment.save()
        BillHistory.objects.create(user=dth_payment.user,
                                   bill_type="DTH",
                                   transaction_id=razorpay_payment_id,
                                   bill_amount=dth_payment.amount,
                                   payment_status="success")

        return redirect("billpay")

    except razorpay.errors.SignatureVerificationError:
        dth_payment.payment_status = "failed"
        dth_payment.save()
        return HttpResponse("Payment verification failed")

    except Exception as e:
        return JsonResponse({"error": f"Something went wrong: {str(e)}"})

from decimal import Decimal

@login_required
def loan_management_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        loan_type = request.POST.get("loan_type")
        loan_amount = request.POST.get("loan_amount")
        loan_duration = request.POST.get("loan_duration")

        if not all([full_name, email, phone_number, loan_type, loan_amount, loan_duration]):
            messages.error(request, "All fields are required.")
            return redirect("loan_management")

        try:
            loan_amount = Decimal(loan_amount)
            loan_duration = int(loan_duration)
        except ValueError:
            messages.error(request, "Invalid input for loan amount or duration.")
            return redirect("loan_management")

        # Save the loan application
        loan = Loanmanagement.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            loan_type=loan_type,
            loan_amount=loan_amount,
            loan_duration=loan_duration
        )

        messages.success(request, "Loan application submitted successfully!")
        return redirect("loan_details", loan_id=loan.id)  # Redirect to details page

    return render(request, "loan_management.html")
@login_required
def loan_details_view(request, loan_id):
    loan = Loanmanagement.objects.get(id=loan_id, user=request.user)  # Fetch the loan record
    return render(request, "loan_details.html", {"loan": loan})






import datetime
def check_cibil_score(request):
    if request.method == "POST":
        
        full_name = request.POST.get("full_name")
        pan_number = request.POST.get("pan_number")
        dob = request.POST.get("dob")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")

        # Dummy logic to generate a CIBIL score (you can replace it with actual logic)
        import random
        score = random.randint(300, 900)

        # Render output page with the calculated score and user details
        context = {
            "name": full_name,
            "account_number": "123456789012",  # You can replace this with actual data
            "pan_number": pan_number,
            "dob": dob,
            "mobile":mobile,
            "email":email,
            "report_date": datetime.datetime.now().strftime("%B %d, %Y"),
            "score": score
        }
        return render(request, "cibil_score_output.html", context)

    return render(request, "cibil_score.html")



from datetime import datetime
from .models import CardRequest



def calculate_age(date_of_birth):
    today = datetime.today().date()
    dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age
@login_required
def submit_card_request(request):
    if request.method == "POST":
        user = request.user  # Ensure this is a valid user object
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to submit a card request.")
            return redirect('login')  # Redirect to login page if not authenticated

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')
        home_address = request.POST.get('home_address')
        card_type = request.POST.get('card_type')  
        adhar_number = request.POST.get('adhar_number')
        annual_income = request.POST.get('annual_income')
        employment_status = request.POST.get('employment_status')

        # Convert income to integer
        try:
            annual_income = int(annual_income)
        except ValueError:
            messages.error(request, "Invalid annual income. Please enter a valid number.")
            return redirect('submit_card_request')

        # Validate age
        age = calculate_age(date_of_birth)
        if age < 18:
            messages.error(request, "You must be at least 18 years old to apply.")
            return redirect('submit_card_request')

        # Validate Credit Card income requirement
        if card_type == "credit" and (annual_income < 100000 or CardRequest.objects.filter(adhar_number=adhar_number).exists()):

            messages.error(request, "Credit Card applicants must have a minimum annual income of 100,000.")
            return redirect('submit_card_request')
        
        

        # Create and save the request
        card_request = CardRequest.objects.create(
            user=user,  # Ensure the user is stored correctly
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            home_address=home_address,
            card_type=card_type,
            adhar_number=adhar_number,
            annual_income=annual_income,
            employment_status=employment_status
        )
        card_request.save()

        messages.success(request, "Card request submitted successfully!")
        return redirect('view_card_request', card_request_id=card_request.id)

    return render(request, 'submit_card_request.html')


@login_required
def view_card_request(request, card_request_id):
    card_request =CardRequest.objects.get( id=card_request_id, user=request.user)
    
    return render(request, 'view_card_request.html', {'card_request': card_request})

def user_logout(request):
    logout(request)  # Logs out the user
    return redirect('index')

      
      



