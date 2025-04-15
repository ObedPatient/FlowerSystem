from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Subscriber
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserDeviceInfo
from .utils import get_client_ip, get_browser_info
from django.contrib.sitemaps import Sitemap
from core.models import Product, CartOrder
from .forms import OrderTrackingForm
from django.urls import reverse

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                # Save the email to the Subscriber model
                subscriber = Subscriber(email=email)
                subscriber.save()

                # Prepare the context for the email template
                context = {'email': subscriber.email}

                # Render the email content using an HTML template
                email_content = render_to_string('Settings/subscription_thank_you.html', context)

                # Define email subject, recipient, and sender
                email_subject = 'Thank You for Subscribing'
                recipient_list = [subscriber.email]
                from_email = settings.EMAIL_HOST_USER

                # Send the email to the subscriber
                send_mail(
                    email_subject,
                    '',  # Leave the plain text message empty if you're using `html_message`
                    from_email,
                    recipient_list,
                    html_message=email_content,
                    fail_silently=False
                )

                # Add a success message
                messages.success(request, 'Thank you for subscribing! Check your email for a confirmation.')

            except Exception as e:
                # Log the error or display a message to the user
                messages.error(request, f"Failed to send email: {e}")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # Redirect to a success page or home page
            return redirect('/')
        else:
            messages.error(request, 'Please enter a valid email address.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Redirect to a default page if not a POST request
    return redirect('/')


def get_username(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})
    return JsonResponse({'username': 'Anonymous'})

@csrf_exempt  # If you want to keep it without CSRF protection
def collect_user_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            timezone = data.get('timezone', 'unknown')
            username = data.get('username', 'Anonymous')  # Default value for username

            # Extract user info
            ip_address = get_client_ip(request)
            browser_info = get_browser_info(request)
            cookies = json.dumps(request.COOKIES)

            # Create and save user info in the database
            user_info = UserDeviceInfo.objects.create(
                ip_address=ip_address,
                browser_info=browser_info,
                timezone=timezone,
                cookies=cookies,
                username=username,  # Now you should get the correct username here
            )

            # Return success response with user ID
            return JsonResponse({'status': 'success', 'user_id': user_info.id})

        except json.JSONDecodeError:
            # Handle invalid JSON error
            return JsonResponse({'status': 'fail', 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            # Catch other exceptions and return an error message
            return JsonResponse({'status': 'fail', 'error': str(e)}, status=500)

    # Return method not allowed if not a POST request
    return JsonResponse({'status': 'fail', 'error': 'Invalid request method'}, status=405)



class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
    
def custom_404_view(request, exception):
    return render(request, 'Not_Found.html', status=404)

def terms_services(request):
    return render(request, 'Settings/terms_services.html')


def approach(request):
    return render(request, 'Settings/approach.html')

def ourCompany(request):
    return render(request, 'Settings/ourCompany.html')



def track_order(request):
    order_status = None
    tracking_info = []

    if request.method == 'POST':
        form = OrderTrackingForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            try:
                order = CartOrder.objects.get(oid=order_id)
                order_status = order.product_status
                
                # Example tracking steps based on order status
                if order_status == "processing":
                    tracking_info = [
                        ("Order Placed", "We have received your order and it is now being processed.", "Completed"),
                    ]
                elif order_status == "out_of_delivery":
                    tracking_info = [
                        ("Order Placed", "We have received your order and it is now being processed.", "Completed"),
                        ("Out for Delivery", "Your order is out for delivery and will arrive soon.", "Pending"),
                    ]
                elif order_status == "delivered":
                    tracking_info = [
                        ("Order Placed", "We have received your order and it is now being processed.", "Completed"),
                        ("Out for Delivery", "Your order is out for delivery and will arrive soon.", "Completed"),
                        ("Delivered", "Your order has been delivered. We hope you enjoy your purchase!", "Completed"),
                    ]
                
                # Redirect to avoid resubmitting the form on refresh (PRG Pattern)
                return redirect(reverse('track_order') + f'?oid={order_id}')
            except CartOrder.DoesNotExist:
                order_status = "Order not found."

    # Handle GET request if redirected (PRG Pattern)
    else:
        order_id = request.GET.get('oid')
        if order_id:
            try:
                order = CartOrder.objects.get(oid=order_id)
                order_status = order.product_status
                
                # Set tracking info based on status (repeat above logic)
                if order_status == "processing":
                    tracking_info = [
                        ("Order Placed", "We have received your order and it is now being processed.", "Completed"),
                    ]
                elif order_status == "out_for_delivery":
                    tracking_info = [
                        ("Order Placed", "We have received your order and it is now being processed.", "Completed"),
                        ("Out for Delivery", "Your order is out for delivery and will arrive soon.", "Pending"),
                    ]
                elif order_status == "delivered":
                    tracking_info = [
                        ("Order Placed", "We have received your order and it is now being processed.", "Completed"),
                        ("Out for Delivery", "Your order is out for delivery and will arrive soon.", "Completed"),
                        ("Delivered", "Your order has been delivered. We hope you enjoy your purchase!", "Completed"),
                    ]
            except CartOrder.DoesNotExist:
                order_status = "Order not found."
        else:
            form = OrderTrackingForm()
        
    form = OrderTrackingForm()  # empty form for GET request
    return render(request, 'Settings/track_order.html', {
        'form': form,
        'order_status': order_status,
        'tracking_info': tracking_info,
        'order_id': order_id
    })


def about_us(request):
    return render(request, 'Settings/about_us.html')