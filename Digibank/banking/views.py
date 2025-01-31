


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from smtplib import SMTPException
import uuid

from .models import CustomerProfile


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
Your account number is: {account_number}

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


from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomerProfile
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        account_number = request.POST.get("account_number")
        password = request.POST.get("password")

        try:
            # Retrieve the user using the account number
            customer = CustomerProfile.objects.get(account_number=account_number)
            user = customer.user  # Get the associated user

            # Authenticate user
            authenticated_user = authenticate(request, username=user.username, password=password)

            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, "Login successful!")
                return redirect("index")  # Redirect to home/dashboard
            else:
                messages.error(request, "Invalid password. Please try again.")

        except CustomerProfile.DoesNotExist:
            messages.error(request, "Account number not found. Please check your details.")

    return render(request, "login.html")

def user_dashboard_view(request):
    return render(request,"user_dashboard.html")




