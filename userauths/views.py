from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userauths.forms import RegistrationForm, ProfileForm, VendorRegistrationForm
from .models import Account, Profile
from Vendor.models import Vendor
from django.views.generic import View
from .utils import TokenGenerator, generate_token
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.urls import NoReverseMatch,reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.mail import BadHeaderError,send_mail
from django.core import mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import requests
import threading
import logging

class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email_message.send(fail_silently=False)
            print("Email sent successfully!")
        except Exception as e:
            logging.error("Failed to send email: %s", e)
            print("Failed to send email:", e)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            # Create the user
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.is_customer = True
            user.is_active = False
            user.save()

            # Prepare email
            current_site = get_current_site(request)
            email_subject = "Activate your account"
            message = render_to_string('userauths/customeractivate.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
            )
            
            # Send email in a separate thread
            EmailThread(email_message).start()

            # Notify user and redirect
            messages.info(request, "Activate by clicking the link sent to your email")
            return redirect('userauths:custom_login')
    else:
        form = RegistrationForm()
         
    context = {
        'form': form,
    }
    return render(request, 'userauths/sign-up.html', context)


def register_vendor(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            # Create the user
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )

            user.phone_number = phone_number
            user.is_vendor = True  # Set the vendor flag
            user.is_active = False  # Deactivate the user until email confirmation
            user.save()  # Now save the user

            if user.is_vendor:  # Assuming you have a field `is_vendor` in your user model
                    Vendor.objects.create(user=user)

            # Prepare the email for account activation
            current_site = get_current_site(request)
            email_subject = "Activate your account"
            message = render_to_string('userauths/vendoractivate.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,  # Added from_email parameter here
                [user.email],
            )
            
            # Send the email in a separate thread
            EmailThread(email_message).start()

            # Notify user and redirect
            messages.info(request, "Activate your account by clicking the link sent to your email")
            return redirect('userauths:custom_login')
    else:
        form = VendorRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'userauths/vendor_register.html', context)


class VendorActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=Account.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
           user.is_active=True
           user.save() 
           messages.info(request,"account activated succcessfully")
           return redirect('userauths:custom_login')
        return render(request,'activatefail.html')  
    

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=Account.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
           user.is_active=True
           user.save() 
           messages.info(request,"account activated succcessfully")
           return redirect('userauths:custom_login')
        return render(request,'activatefail.html')  
      
def custom_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Check if the email exists in the user database
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, 'Failed to login. Email does not exist.')
            return redirect('userauths:custom_login')

        # Authenticate the user
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            auth.login(request, user)

            # Check if the user is part of the 'Sellers' group
            if user.groups.filter(name='Sellers').exists():
                return redirect('vendorDashboard')  # Replace with the actual vendor dashboard URL name
            elif user.is_customer:  # Assuming you have a method to identify customer
                return redirect('product_list_view')  # Replace with the actual customer dashboard URL name
            else:
                return redirect('Home')  # Default redirect if no specific role is identified
        else:
            messages.error(request, 'Failed to login. Invalid email or password.')
            return redirect('userauths:custom_login')

    # Add warning message if redirected from a protected page        
    if 'next' in request.GET:
        messages.warning(request, 'You need to log in to access this page.')

    # Get the next URL from the query parameters and pass it to the template
    next_url = request.GET.get('next', '')
    return render(request, 'userauths/custom_login.html', {'next': next_url})


@login_required()
def custom_logout(request):
    auth.logout(request)
    messages.success(request, 'You are Logged out.')
    return render(request, 'userauths/custom_login.html')

class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'userauths/request_reset_email.html')
    
    def post(self,request):
        email=request.POST['email']
        user=Account.objects.filter(email=email)

        if user.exists():
            current_site=get_current_site(request)
            email_subject='[reset your password]'
            message=render_to_string('userauths/reset_user_password.html',
            {
                'domain':'127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token':PasswordResetTokenGenerator().make_token(user[0])
            })

            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
            EmailThread(email_message).start()
            
            messages.info(request,"we have sent you email with instructions on how to reset password")
            return render(request,'userauths/request_reset_email.html')
        
class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token
        }  
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=Account.objects.get(pk=user_id)  

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset is invalid link") 
                return render(request,'userauths/request_reset_email.html')

        except DjangoUnicodeDecodeError as identifier:
            pass 
        return render(request,'userauths/set_new_password.html',context)
    
    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token
        }
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password !=confirm_password:
            messages.warning(request,"Password Is Not Matching")
            return render(request,'userauths/set_new_password.html',context)
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=Account.objects.get(pk=user_id) 
            user.set_password(password)
            user.save()
            messages.success(request,"Password Reset Success Please Login With New Password")
            return redirect('userauths:custom_login')
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,"Something Went Wrong")
            return render(request,'userauths/set_new_password.html',context)
       


def profile_update(request):
    # Get the user's profile
    profile = Profile.objects.get(user=request.user)
    
    if request.method == "POST":
        # Initialize the form with POST data and uploaded files
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save the form but don't commit to the database yet
            new_form = form.save(commit=False)
            new_form.user = request.user
            
            # Check if profile_image is provided or not
            if not new_form.profile_image:
                # Handle missing profile_image logic if necessary
                pass
            
            # Save the profile
            new_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("dashboard")
        else:
            # Reinitialize the form with existing data if validation fails
            form = ProfileForm(instance=profile)
    else:
        # Initialize the form with existing data for GET request
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }
    return render(request, "userauths/profile_update.html", context)
