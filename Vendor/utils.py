import hashlib
import threading
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Vendor, Service
from core.utils import get_exchange_rate, convert_currency


def generate_transaction_id(user_id, payment_method, amount):
    # Concatenate user_id, payment_method, and amount to generate a unique string
    raw_string = f'{user_id}{payment_method}{amount}'
    # Create a SHA256 hash of the string
    transaction_id = hashlib.sha256(raw_string.encode()).hexdigest()
    return transaction_id

class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send(fail_silently=False)





def get_vendor_status(request):
    if not request.user.is_authenticated:
        return None, redirect('userauths:custom_login')

    # Check if user is in "sellers" group
    if not request.user.groups.filter(name='Sellers').exists():
        return None, redirect('userauths:custom_login')

    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        return None, render(request, 'Vendor/vendorDashboard.html')

    
    

    return vendor, None
