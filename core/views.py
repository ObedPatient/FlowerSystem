import json
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg 
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from taggit.models import Tag
from django.utils import timezone
from core.forms import ProductReviewForm
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from core.models import Coupon, Product, ProductImages,ProductReview, CartOrder, CartOrderItem, Category, WishList, Address, VendorOrder
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.http import require_POST
from django.db.models.functions import ExtractMonth
import calendar
from Vendor.models import Vendor
from userauths.models import Contact, Profile
from django.core import serializers
import requests
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date


import threading
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from .utils import TokenGenerator, generate_token, convert_currency, get_exchange_rate
from django.core.paginator import Paginator


class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        super().__init__()

    def run(self):
        try:
            self.email_message.send()
        except Exception as e:
            # Handle or log the exception
            print(f"Error sending email: {e}")





def Home(request):
    products = Product.objects.filter(product_status="published", featured=True)
    recent_date = datetime.now() - timedelta(days=30)
    new_arrivals = Product.objects.filter(product_status="published", date__gte=recent_date)
    selected_currency = request.session.get('currency', 'USD')

    # Fetch latest exchange rates for USD (assumed base currency)
    exchange_rates = get_exchange_rate('USD')

    # Convert prices of each product to the selected currency
    for product in products:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

    for product in new_arrivals:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

    
    context = {
        'products':products, 
        'selected_currency': selected_currency,
        'new_arrivals': new_arrivals,  # Optional: add pagination for new_arrivals if needed
    }

    return render(request, 'Home.html', context)


def Not_Found(request):
    return render(request, 'Not_Found.html')



def product_list_view(request):
    products = Product.objects.filter(product_status="published")
    selected_currency = request.session.get('currency', 'USD')

    # Fetch latest exchange rates for USD (assumed base currency)
    exchange_rates = get_exchange_rate('USD')

    # Convert prices of each product to the selected currency
    for product in products:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

    

    context = {
        'products':products,  
        'selected_currency': selected_currency,
    }
    
    return render(request, 'Core/Store.html', context)


def Category_list_view(request):
    categories = Category.objects.all()

    context = {
        'categories':categories,
    }

    return render(request, 'Core/category.html', context)

def All_vendors(request):
    vendors = Vendor.objects.all()  
    
    context = {
        'vendors':vendors,
    }
    
    return render(request, 'Core/All_vendors.html', context)

def product_by_category(request, id, slug):
    # Use get_object_or_404 to handle non-existing categories gracefully
    category = get_object_or_404(Category, id=id, slug=slug)
    
    # Fetch all products in the category and its subcategories
    products = Product.objects.filter(product_status='published', category__in=category.get_descendants(include_self=True))
    
    selected_currency = request.session.get('currency', 'USD')

    # Fetch latest exchange rates for USD (assumed base currency)
    exchange_rates = get_exchange_rate('USD')

    # Convert prices of each product to the selected currency
    for product in products:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

   

    context = {
        'products':products,
        'category': category,
        'selected_currency': selected_currency,
    }

    return render(request, 'Core/product_by_category.html', context)


def subcategory_view(request, category_id, category_slug):
    subcategory = get_object_or_404(Category, id=category_id, slug=category_slug)
    selected_currency = request.session.get('currency', 'USD')

    # Fetch latest exchange rates for USD (assumed base currency)
    exchange_rates = get_exchange_rate('USD')

    products = subcategory.category.all()  # Get all products in the subcategory

    # Convert prices of each product to the selected currency
    for product in products:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

    

    context = {
        'products':products,
        'subcategory': subcategory,
        'selected_currency': selected_currency,
    }

    return render(request, 'Core/subcategory_view.html', context)


def set_currency(request, currency_code):
    request.session['currency'] = currency_code
    return redirect(request.META.get('HTTP_REFERER', '/'))

def vendor_list(request):
    vendors = Vendor.objects.all()

    context = {
        'vendors':vendors,
    }
    return render(request, 'Core/vendor_list.html', context)


def vendor_detail_view(request, vid):
    vendor = get_object_or_404(Vendor, vid=vid)  # Use get_object_or_404 for safer querying
    products = Product.objects.filter(vendor=vendor, product_status="published")

    selected_currency = request.session.get('currency', 'USD')

    # Fetch latest exchange rates for USD (assumed base currency)
    exchange_rates = get_exchange_rate('USD')

    # Convert prices of each product to the selected currency
    for product in products:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

    

    context = {
        'products':products,
        'vendor': vendor,
        'selected_currency': selected_currency,
    }

    return render(request, 'Core/vendor_detail.html', context)


def product_detail_view(request, pid, slug):
    # Fetch the product details
    product = get_object_or_404(Product, pid=pid, slug=slug)
    selected_currency = request.session.get('currency', 'USD')
    p_image = product.p_images.all()
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    user = request.user

    # Initialize the variable for purchased status
    has_purchased = False

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the user has purchased the product
        has_purchased = CartOrderItem.objects.filter(
            order__user=user,  # Use request.user instead of user
            product=product,
            order__paid_status=True  # Ensure the order is marked as paid
        ).exists()

    # Fetch product reviews and calculate average rating
    reviews = ProductReview.objects.filter(product=product).order_by('-date')
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Handle currency conversion
      # Default to USD if not set
    exchange_rates = get_exchange_rate('USD')  # Fetch latest exchange rates
    price_in_selected_currency = convert_currency(product.price, 'USD', selected_currency, exchange_rates)

    for p in products:
        p.converted_price = convert_currency(p.price, 'USD', selected_currency, exchange_rates)
        p.converted_old_price = convert_currency(p.old_price, 'USD', selected_currency, exchange_rates)

    if price_in_selected_currency is None:
        # Fallback to the original price if conversion fails
        price_in_selected_currency = product.price

    # Determine if the user can make a review
    review_form = ProductReviewForm()
    make_review = True
    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()
        if user_review_count > 0:
            make_review = False

    context = {
        'reviews': reviews,
        'product': product,
        'make_review': make_review,
        'products': products,
        'p_image': p_image,
        'review_form': review_form,
        'average_rating': average_rating,
        'price': price_in_selected_currency,
        'currency': selected_currency,
        'has_purchased': has_purchased
    }

    return render(request, 'Core/single_product.html', context)

def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by('-id')
    selected_currency = request.session.get('currency', 'USD')

    # Fetch latest exchange rates for USD (assumed base currency)
    exchange_rates = get_exchange_rate('USD')

    # Convert prices of each product to the selected currency
    for product in products:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

    tag = None 
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

   
    context = {
        'products':products,  # Use page_obj instead of products
        'tag': tag,
        'selected_currency': selected_currency,
    }

    return render(request, 'Core/tag.html', context)


def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user
    
    review = ProductReview.objects.create(
        user = user,
        product = product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user':user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    return JsonResponse(
        {
        'bool': True,
        'context':context,
        'average_reviews': average_reviews,
        }
    )

def search_view(request):
    query = request.GET.get("q", "").strip()  # Clean up the query
    catid = request.GET.get("catid", "")  # Get category ID

    print(f"Query: '{query}'")  # Debugging: Output the query
    print(f"Category ID: '{catid}'")  # Debugging: Output category ID

    # Initialize products to an empty queryset
    products = Product.objects.none()

    # Check if both query and category are provided
    if query and catid and int(catid) > 0:
        # Filter by both query and category
        products = Product.objects.filter(title__icontains=query, category_id=catid).order_by("-date")
    elif query:
        # If only query is provided
        products = Product.objects.filter(title__icontains=query).order_by("-date")
    elif catid and int(catid) > 0:
        # If only category is provided
        products = Product.objects.filter(category_id=catid).order_by("-date")

    if not products.exists():
        print("No products found.")  # Check if products are found

    category = Category.objects.filter(id=catid).first() if catid and int(catid) > 0 else None

    # Handle currency conversion
    selected_currency = request.session.get('currency', 'USD')
    exchange_rates = get_exchange_rate('USD')

    for product in products:
        product.converted_price = convert_currency(product.price, 'USD', selected_currency, exchange_rates)
        product.converted_old_price = convert_currency(product.old_price, 'USD', selected_currency, exchange_rates)

    context = {
        'products': products,
        'query': query,
        'selected_currency': selected_currency,
        # Add the category here
        'category': category,
    }
    
    return render(request, 'Core/search.html', context)


def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")
    print("Received categories:", categories)
    print("Received vendors:", vendors)

   


    min_price = float(request.GET.get('min_price', 0))
    max_price = float(request.GET.get('max_price', float('inf')))

    products = Product.objects.filter(product_status="published").order_by("-id").distinct()
    products = products.filter(price__gte=min_price, price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()

    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})


from decimal import Decimal, InvalidOperation

def add_to_cart(request):
    base_currency = 'USD'
    rates = get_exchange_rate(base_currency)  # Get the latest rates

    # Extract details from the request
    product_id = str(request.GET.get('id'))
    title = request.GET.get('title')
    slug = request.GET.get('slug')
    qty = int(request.GET.get('qty'))

    # Retrieve and clean the price parameter
    raw_price = request.GET.get('price', '0')  # Default to '0' if price is not found

    # Refine the price cleanup logic to handle multiple decimal points
    cleaned_price = ''
    found_decimal = False
    for char in raw_price:
        if char.isdigit():
            cleaned_price += char
        elif char == '.' and not found_decimal:
            # Allow only the first decimal point
            cleaned_price += char
            found_decimal = True

    print(f"Cleaned Price: {cleaned_price}")  # Debugging line

    # Attempt to convert the cleaned price to Decimal
    try:
        price = Decimal(cleaned_price)
    except InvalidOperation:
        return JsonResponse({"error": "Invalid price format."}, status=400)

    currency = request.GET.get('currency')  # Currency of the product price
    image = request.GET.get('image')
    pid = request.GET.get('pid')

    # Print the original price
    print(f"Original Price: {price} {currency}")  # Debugging line

    # Convert the price to USD if necessary
    if currency != base_currency:
        print(f"Converting {price} {currency} to {base_currency} using rates: {rates}")
        converted_price = convert_currency(price, currency, base_currency, rates)
        if converted_price is not None:
            print(f"Converted Price: {converted_price} {base_currency}")  # Debugging line
            price = converted_price  # Use the converted price
        else:
            return JsonResponse({"error": "Currency conversion failed."}, status=400)

    # Prepare the cart product dictionary
    cart_product = {
        product_id: {
            'title': title,
            'slug': slug,
            'qty': qty,
            'price': float(price),  # Store price in USD
            'currency': base_currency,  # Store the currency as USD
            'image': image,
            'pid': pid,
        }
    }

    # Update the session with cart data
    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        if product_id in cart_data:
            # Update the quantity of the existing product
            cart_data[product_id]['qty'] += qty
        else:
            # Add new product to the cart
            cart_data.update(cart_product)
        request.session['cart_data_obj'] = cart_data
    else:
        # Initialize cart data if not present
        request.session['cart_data_obj'] = cart_product

    return JsonResponse({
        "data": request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj'])
    })




def cart(request):
    cart_total_amount = Decimal('0.00')  # Use Decimal for accurate calculations
    selected_currency = request.session.get('currency', 'USD')  # Get the selected currency (default to USD)
    
    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Ensure this returns a dict with currency as keys
    
    if 'cart_data_obj' in request.session:
        # Iterate over the items in the cart
        for product_id, item in request.session['cart_data_obj'].items():
            # Convert the price from USD to the selected currency
            original_price = Decimal(item['price'])  # Assuming item['price'] is stored in USD
            
            # Ensure convert_currency handles missing currency gracefully
            if selected_currency in exchange_rates:
                converted_price = convert_currency(original_price, 'USD', selected_currency, exchange_rates)
            else:
                # Handle cases where the currency isn't in the rates (could log a warning)
                converted_price = original_price  # Default to original price
            
            # Update the item price in the cart session data (not permanent, just for display)
            item['converted_price'] = converted_price
            
            # Calculate the total amount using the converted price
            cart_total_amount += Decimal(item['qty']) * converted_price  # Keep it as Decimal for precision
        
        return render(request, 'Core/cart.html', {
            "cart_data": request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': round(cart_total_amount, 2),  # Round for display
            'selected_currency': selected_currency,  # Pass the selected currency to the template
        })
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("Home")



def delete_from_cart(request):
    product_id = str(request.GET['id'])
    selected_currency = request.session.get('currency', 'USD')  # Get the selected currency (default to USD)
    
    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Fetch exchange rates relative to 1 USD

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            # Convert the price from USD to the selected currency
            converted_price = convert_currency(float(item['price']), 'USD', selected_currency, exchange_rates)
            item['converted_price'] = float(converted_price)  # Convert Decimal to float
            # Calculate the total amount using the converted price
            cart_total_amount += int(item['qty']) * float(converted_price)

    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': float(cart_total_amount),  # Ensure cart_total_amount is a float
        'selected_currency': selected_currency,
    })
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})



def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']
    selected_currency = request.session.get('currency', 'USD')  # Get the selected currency (default to USD)
    
    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[product_id]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for product_id, item in request.session['cart_data_obj'].items():
            # Convert the price from USD to the selected currency
            converted_price = convert_currency(float(item['price']), 'USD', selected_currency, exchange_rates)
            item['converted_price'] = float(converted_price)  # Convert Decimal to float
            # Calculate the total amount using the converted price
            cart_total_amount += int(item['qty']) * float(converted_price)

    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': float(cart_total_amount),  # Ensure cart_total_amount is a float
        'selected_currency': selected_currency,
    })
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


@login_required
def checkout(request):
    cart_total_amount = 0
    cart_data = request.session.get('cart_data_obj', {})
    selected_currency = request.session.get('currency', 'USD')  # Default to USD if not set

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Assume this gives rates relative to 1 USD

    # Convert cart data to selected currency and calculate total
    converted_cart_data = {}
    
    for product_id, item in cart_data.items():
        original_price = float(item['price'])  # Assuming item['price'] is in USD
        converted_price = convert_currency(original_price, 'USD', selected_currency, exchange_rates)
        item_total = int(item['qty']) * converted_price
        
        # Update the item data with converted prices
        converted_cart_data[product_id] = {
            'title': item['title'],
            'image': item['image'],
            'qty': item['qty'],
            'price': converted_price,
            'total': item_total,
            'pid': item.get('pid')
        }
        
        # Calculate the total amount using the converted price
        cart_total_amount += item_total

    context = {
        'cart_data': converted_cart_data,
        'totalcartitems': len(cart_data),
        'cart_total_amount': cart_total_amount,
        'selected_currency': selected_currency,  # Pass the selected currency to the template
    }

    return render(request, 'Core/checkout.html', context)

def place_order(request):
    cart_total_amount = 0
    shipping_fee = 0

    if request.method == 'POST':
        # Collecting bio details
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        city = request.POST.get("city")  # Retrieve city information
        country = request.POST.get("country")

        # Storing bio details in session
        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['phone_number'] = phone_number
        request.session['address'] = address
        request.session['city'] = city
        request.session['country'] = country

        # Calculate the shipping fee based on the city
        kigali_districts = ['Nyarugenge', 'Gasabo', 'Kicukiro']  # Define Kigali districts

        if city in kigali_districts:
            shipping_fee = 1.32   # Low shipping fee for Kigali
        else:
            shipping_fee = 1.61  # High shipping fee for other districts

        if 'cart_data_obj' in request.session:
            cart_data = request.session['cart_data_obj']

            # Calculating total amount
            for product_id, item in cart_data.items():
                cart_total_amount += int(item['qty']) * float(item['price'])

            # Adding the shipping fee to the cart total amount
            cart_total_amount += shipping_fee

            # Creating the order
            order = CartOrder.objects.create(
                user=request.user,
                price=cart_total_amount,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                address=address,
                city=city,
                country=country,
                shipping_fee=shipping_fee,  # Save the shipping fee in the order
            )

            # Creating CartOrderItem entries
            for product_id, item in cart_data.items():
                product = get_object_or_404(Product, id=product_id)  # Ensure product exists

                CartOrderItem.objects.create(
                    order=order,
                    product=product,  # Associate the product correctly
                    invoice_no="INVOICE_NO_" + str(order.id),
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price']),
                )

            # Clearing session data safely
            keys_to_delete = ['full_name', 'email', 'phone_number', 'address', 'city', 'country']
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]

            # Redirect to payment view
            return redirect("payment_view", order.oid)

    return redirect("payment_view", order.oid)


@login_required
def payment_view(request, oid):
    order = get_object_or_404(CartOrder, oid=oid)
    order_items = CartOrderItem.objects.filter(order=order)

    # Retrieve the selected currency from the session
    selected_currency = request.session.get('currency', 'USD')  # Default to USD if not set

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')

    # Convert order total and saved amount to the selected currency
    original_price = Decimal(order.price)
    converted_price = Decimal(convert_currency(original_price, 'USD', selected_currency, exchange_rates))

    saved_amount = Decimal(order.saved)
    converted_saved_amount = Decimal(convert_currency(saved_amount, 'USD', selected_currency, exchange_rates))

    # Convert item prices to selected currency and calculate total
    converted_order_items = []
    total_price_before_discount = Decimal(0)

    for item in order_items:
        original_price = Decimal(item.price)
        converted_price = Decimal(convert_currency(original_price, 'USD', selected_currency, exchange_rates))
        item_total = item.qty * converted_price
        total_price_before_discount += item_total

        converted_order_items.append({
            'product': item.product,
            'qty': item.qty,
            'price': converted_price,
            'total': item_total,
        })

    # Add the shipping fee to the total price
    shipping_fee_in_selected_currency = Decimal(convert_currency(Decimal(order.shipping_fee), 'USD', selected_currency, exchange_rates))
    total_price_before_discount += shipping_fee_in_selected_currency

    # Final price calculation without any discount/coupon
    final_price = total_price_before_discount.quantize(Decimal('0.01'))  # Round to two decimal places

    context = {
        "order": order,
        "order_items": converted_order_items,
        "converted_order_total": final_price,
        "selected_currency": selected_currency,
        "converted_saved_amount": converted_saved_amount,
        "shipping_fee": shipping_fee_in_selected_currency,
    }

    return render(request, "Core/payment_view.html", context)


@login_required
def payment_completed_view(request, oid):
    # Fetch the order using the order ID
    order = get_object_or_404(CartOrder, oid=oid)
    order_items = CartOrderItem.objects.filter(order=order)

    # Retrieve the selected currency from the session
    selected_currency = request.session.get('currency', 'USD')

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')

    # Convert order total to selected currency
    original_price = order.price
    converted_order_total = convert_currency(original_price, 'USD', selected_currency, exchange_rates)

    # Convert saved amount to selected currency
    saved_amount = order.saved
    converted_saved_amount = convert_currency(saved_amount, 'USD', selected_currency, exchange_rates)

    # Convert shipping fee and final price to selected currency
    shipping_fee = order.shipping_fee
    converted_shipping_fee = convert_currency(shipping_fee, 'USD', selected_currency, exchange_rates)

    final_price = order.final_price
    converted_final_price = convert_currency(final_price, 'USD', selected_currency, exchange_rates)

    for order_item in order_items:
            order_item.converted_price = convert_currency(order_item.price, 'USD', selected_currency, exchange_rates)
            order_item.converted_total_price = convert_currency(order_item.total, 'USD', selected_currency, exchange_rates)

    payment_method = request.GET.get('payment_method', 'Unknown')

    # Check if the payment is not yet marked as completed
    if not order.paid_status:
        # Mark the order as paid
        order.paid_status = True
        order.payment_method = payment_method  # Save the payment method
        order.save()

        selected_currency = request.session.get('currency', 'USD')
        send_admin_payment_notification(order, selected_currency)

        # Set commission rate
        commission_rate = Decimal('0.10')  # 10% commission as a Decimal

        # Dictionary to store commission details for each vendor
        vendor_commissions = {}

        for cart_item in order_items:
            product = cart_item.product
            vendor = product.vendor

            # Reduce stock for the product
            product.in_stock -= cart_item.qty
            if product.in_stock <= 0:
                product.in_stock = 0
                product.product_status = "disabled"
            product.save()

            # Calculate the item's total price
            item_total_price = Decimal(cart_item.qty) * Decimal(cart_item.price)
            converted_item_total = convert_currency(item_total_price, 'USD', selected_currency, exchange_rates)

            # Calculate commission and net amount
            commission = converted_item_total * commission_rate
            net_amount = converted_item_total - commission

            # Store commission details for each vendor (for multiple products from the same vendor)
            if vendor not in vendor_commissions:
                vendor_commissions[vendor] = {
                    'total_amount': Decimal('0.00'),
                    'total_commission': Decimal('0.00'),
                    'net_amount': Decimal('0.00')
                }

            # Aggregate commission and net amount for each vendor
            vendor_commissions[vendor]['total_amount'] += converted_item_total
            vendor_commissions[vendor]['total_commission'] += commission
            vendor_commissions[vendor]['net_amount'] += net_amount

        # Create VendorOrder records for each vendor
        for vendor, amounts in vendor_commissions.items():
            try:
                VendorOrder.objects.create(
                    vendor=vendor,
                    cart_order=order,
                    total_amount=amounts['total_amount'],
                    commission=amounts['total_commission'],
                    net_amount=amounts['net_amount']
                )
            except Exception as e:
                print(f"Error creating VendorOrder for {vendor}: {e}")

        # Clear session cart data
        if 'cart_data_obj' in request.session:
            del request.session['cart_data_obj']

        # Prepare email to the user
        email_subject = "Order Confirmation"
        message = render_to_string('Core/order_confirmation_email.html', {
            'user': order.user,
            'order': order,
            'order_items': order_items,  # Pass converted order items
            'domain': get_current_site(request).domain,
            'converted_order_total': converted_order_total,  # Include converted total in email
            'selected_currency': selected_currency,
            "converted_saved_amount": converted_saved_amount,
            "converted_shipping_fee": converted_shipping_fee,
            "final_price": converted_final_price,
        })
        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [order.user.email],
        )
        email_message.content_subtype = "html"

        # Send email in a separate thread
        try:
            EmailThread(email_message).start()
        except Exception as e:
            messages.error(request, "Order completed but email could not be sent. Please contact support.")

        # Notify user and redirect
        messages.info(request, "Your order has been completed and an email confirmation has been sent.")

    context = {
        "order": order,
        "order_items": order_items,  # Use converted order items
        "converted_order_total": converted_order_total,  # Converted total price
        "selected_currency": selected_currency,  # Currency for display
        "converted_saved_amount": converted_saved_amount,
        "converted_shipping_fee": converted_shipping_fee,
        "final_price": converted_final_price,
    }

    return render(request, 'Core/payment_completed_view.html', context)

def send_admin_payment_notification(order, selected_currency):
    """Send an email to the admin when a payment is completed successfully."""

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Assume this gives rates relative to 1 USD

    try:
        subject = f"Order #{order.oid} - Payment Completed"

        total_price = convert_currency(order.price, 'USD', selected_currency, exchange_rates)
        saved_amount = convert_currency(order.saved, 'USD', selected_currency, exchange_rates)

        context = {
            'order_id': order.oid,
            'customer_name': order.full_name,
            'customer_email': order.email,
            'total_price': total_price,  # Converted price
            'saved_amount': saved_amount,  # Converted saved amount
            'order_date': order.order_date,
            'selected_currency': selected_currency,
        }

        # Render the HTML template with context data
        html_message = render_to_string('Core/Emails/admin_notification.html', context)

        # Send the HTML email
        email = EmailMessage(
            subject,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        email.content_subtype = 'html'  # Send the email as HTML
        email.send(fail_silently=False)  # Set to False to raise errors on failure
        print("Email sent successfully to the admin.")

    except Exception as e:
        print(f"Failed to send email: {e}")




@login_required
def order_confirmation(request, oid):
    order = get_object_or_404(CartOrder, oid=oid)
    order_items = CartOrderItem.objects.filter(order=order)

    # Retrieve the selected currency from the session
    selected_currency = request.session.get('currency', 'USD')  # Default to USD if not set

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Assume this gives rates relative to 1 USD

    for order_item in order_items:
        order_item.converted_price = convert_currency(order_item.price, 'USD', selected_currency, exchange_rates)
        order_item.converted_total_price = convert_currency(order_item.total, 'USD', selected_currency, exchange_rates)

    # Convert order total to selected currency
    original_price = order.price
    converted_order_total = convert_currency(original_price, 'USD', selected_currency, exchange_rates)

    # Convert saved amount to selected currency
    saved_amount = order.saved
    converted_saved_amount = convert_currency(saved_amount, 'USD', selected_currency, exchange_rates)

    shipping_fee = order.shipping_fee
    converted_shipping_fee = convert_currency(shipping_fee, 'USD', selected_currency, exchange_rates)

    final_price = order.final_price
    converted_final_price = convert_currency(final_price, 'USD', selected_currency, exchange_rates)

    payment_method = request.GET.get('payment_method', 'Unknown')  # Default to 'Unknown' if not provided

    # Check if the payment is not yet marked as completed
    if not order.paid_status:
        # Mark the order as paid
        order.paid_status = False
        order.payment_method = payment_method  # Save the payment method
        order.save()

        selected_currency = request.session.get('currency', 'USD')
        send_admin_payment_notification(order, selected_currency)
        
        # Commission rate
        commission_rate = Decimal('0.10')  # 10% commission

        vendor_commissions = {}  # Dictionary to store vendor commissions

        for cart_item in order_items:
            product = cart_item.product
            vendor = product.vendor

            # Reduce stock for the product
            product.in_stock -= cart_item.qty
            if product.in_stock <= 0:
                product.in_stock = 0
                product.product_status = "disabled"
            product.save()

            # Calculate total price for the item in the selected currency
            item_total_price = convert_currency(Decimal(cart_item.total), 'USD', selected_currency, exchange_rates)

            # Calculate 10% commission for this product
            commission = item_total_price * commission_rate
            net_amount = item_total_price - commission

            # Store commission details for each vendor (for multiple products from the same vendor)
            if vendor not in vendor_commissions:
                vendor_commissions[vendor] = {
                    'total_amount': Decimal('0.00'),
                    'total_commission': Decimal('0.00'),
                    'net_amount': Decimal('0.00')
                }

            # Aggregate commission and net amount for each vendor
            vendor_commissions[vendor]['total_amount'] += item_total_price
            vendor_commissions[vendor]['total_commission'] += commission
            vendor_commissions[vendor]['net_amount'] += net_amount

        # Create VendorOrder records for each vendor
        for vendor, amounts in vendor_commissions.items():
            try:
                VendorOrder.objects.create(
                    vendor=vendor,
                    cart_order=order,
                    total_amount=amounts['total_amount'],
                    commission=amounts['total_commission'],
                    net_amount=amounts['net_amount']
                )
            except Exception as e:
                print(f"Error creating VendorOrder for {vendor}: {e}")

        # Clear session cart data
        if 'cart_data_obj' in request.session:
            del request.session['cart_data_obj']

        # Prepare email to the user
        email_subject = "Order Confirmation"
        message = render_to_string('Core/order_confirmation_email.html', {
            'user': order.user,
            'order': order,
            'order_items': order_items,
            'domain': get_current_site(request).domain,
            'converted_order_total': converted_order_total,  # Include converted total in email
            'selected_currency': selected_currency,
            "converted_saved_amount": converted_saved_amount,
            "converted_shipping_fee": converted_shipping_fee,
            "final_price": converted_final_price,
        })
        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [order.user.email],
        )
        email_message.content_subtype = "html"

        # Send email in a separate thread
        try:
            EmailThread(email_message).start()
        except Exception as e:
            messages.error(request, "Order completed but email could not be sent. Please contact support.")

        # Notify user and redirect
        messages.info(request, "Your order has been completed and an email confirmation has been sent.")

    context = {
        "order": order,
        "order_items": order_items,  # Use converted order items
        'converted_order_total': converted_order_total,  # Include converted total in email
        'selected_currency': selected_currency,
        "converted_saved_amount": converted_saved_amount,
        "converted_shipping_fee": converted_shipping_fee,
        "final_price": converted_final_price,
    }

    return render(request, 'Core/order_confirmation.html', context)


@login_required
def payment_failed_view(request, oid):
    order = get_object_or_404(CartOrder, oid=oid)
    order_items = order.items.all()  # Assuming related name is 'cartorderitem_set'

    selected_currency = request.session.get('currency', 'USD')  # Default to USD if not set

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Assume this gives rates relative to 1 USD

    original_price = order.price
    converted_order_total = convert_currency(original_price, 'USD', selected_currency, exchange_rates)

    # Convert saved amount to selected currency
    saved_amount = order.saved
    converted_saved_amount = convert_currency(saved_amount, 'USD', selected_currency, exchange_rates)

    shipping_fee = order.shipping_fee
    Converted_shipping_fee = convert_currency(shipping_fee, 'USD', selected_currency, exchange_rates)

    final_price = order.final_price
    converted_final_price = convert_currency(final_price, 'USD', selected_currency, exchange_rates)


    for order_item in order_items:
        order_item.converted_price = convert_currency(order_item.price, 'USD', selected_currency, exchange_rates)
        order_item.converted_total_price = convert_currency(order_item.total, 'USD', selected_currency, exchange_rates)
    
    context = {
        'order': order,
        'order_items': order_items,
        'selected_currency': selected_currency,
        'converted_order_total': converted_order_total,
        "converted_saved_amount": converted_saved_amount,  # Converted saved amount
        "Converted_shipping_fee": Converted_shipping_fee,
        "final_price": converted_final_price,
    }
    
    return render(request, 'Core/payment_failed_view.html', context)

@login_required
def dashboard(request):
    orders = CartOrder.objects.filter(user=request.user).order_by('-id')
    address = Address.objects.filter(user=request.user)

    selected_currency = request.session.get('currency', 'USD')  # Default to USD if not set

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Assume this gives rates relative to 1 USD

    for order in orders:
        order.converted_price = convert_currency(order.price, 'USD',  selected_currency, exchange_rates)

    orderz = CartOrder.objects.annotate(month=ExtractMonth("order_date")).values("month").annotate(count=Count("id")).values("month", "count")

    # Lists to store months and total orders
    months = []
    total_orders = []

    # Iterate through the result set
    for i in orderz:
        months.append(calendar.month_name[i["month"]])  # Get the month name
        total_orders.append(i["count"])  

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, "Address Added Successfully.")
        return redirect('dashboard')
    else:
        pass

    profile = Profile.objects.get(user=request.user)
    
    context = {
        "profile": profile,
        "orders": orders,
        "months": months,
        "total_orders": total_orders,
        "selected_currency": selected_currency,
        "orderz": orderz,
        "address": address,  # renamed to addresses for clarity
    }
    return render(request, 'Core/dashboard.html', context)


def account_orders_view(request):
    orders = CartOrder.objects.filter(user=request.user).order_by('-id')
    
    # Currency handling
    selected_currency = request.session.get('currency', 'USD')
    exchange_rates = get_exchange_rate('USD')

    # Apply filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    invoice_no = request.GET.get('invoice_no')

    if start_date:
        parsed_start_date = parse_date(start_date)
        if parsed_start_date:
            orders = orders.filter(order_date__gte=parsed_start_date)
    
    if end_date:
        parsed_end_date = parse_date(end_date)
        if parsed_end_date:
            orders = orders.filter(order_date__lte=parsed_end_date)

    if invoice_no:
        # Extract the numeric ID from the invoice number (e.g., "#INVOICE_NO-2123" -> "123")
        try:
            # Assuming format is "#INVOICE_NO-2" followed by the ID
            invoice_id = int(invoice_no.replace('#INVOICE_NO-2', '').strip())
            orders = orders.filter(id=invoice_id)
        except (ValueError, AttributeError):
            # If the input is invalid, return no results or handle gracefully
            orders = orders.none()

    # Convert prices for each order
    for order in orders:
        order.converted_price = convert_currency(order.price, 'USD', selected_currency, exchange_rates)

    # Handle AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        orders_data = [
            {
                'id': order.id,
                'order_date': order.order_date.strftime('%Y-%m-%d'),
                'product_status': order.product_status,
                'converted_price': f"{order.converted_price:,}",
                'paid_status': order.paid_status,
            }
            for order in orders
        ]
        return JsonResponse({
            'orders': orders_data,
            'selected_currency': selected_currency,
        })

    # Non-AJAX request
    context = {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
        'invoice_no': invoice_no,
        'selected_currency': selected_currency,
    }
    return render(request, 'Core/dashboard.html', context)

@login_required
def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItem.objects.filter(order=order)

    selected_currency = request.session.get('currency', 'USD')  # Default to USD if not set

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Assume this gives rates relative to 1 USD

    for order in order_items:
        order.converted_price = convert_currency(order.price, 'USD', selected_currency, exchange_rates)
        order.converted_total_price = convert_currency(order.total, 'USD', selected_currency, exchange_rates)

    context = {
        "order_items": order_items,
        "selected_currency": selected_currency,
    }

    return render(request, 'Core/order_detail.html', context)

@login_required
def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})

@login_required
def wishlist_view(request):
    selected_currency = request.session.get('currency', 'USD')  # Default to USD if not set

    # Fetch the latest exchange rates (base currency: USD)
    exchange_rates = get_exchange_rate('USD')  # Assume this gives rates relative to 1 USD
    
    # Fetch wishlist items for the logged-in user
    wishlist = WishList.objects.filter(user=request.user).select_related('product')
    
    for w in wishlist:
        w.converted_price = convert_currency(w.product.price, 'USD', selected_currency, exchange_rates)

    context = {
        'wishlist': wishlist,
        'selected_currency': selected_currency,
    }

    return render(request, "Core/wishlist_view.html", context)


def add_to_wishlist(request):
    id = request.GET['id']
    
    product = Product.objects.get(id=id)

    wishlist_count = WishList.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool": True,
            "wishlist_count": WishList.objects.filter(user=request.user).count()  # Updated count
        }
    else:
        new_wishlist = WishList.objects.create(
            product=product,
            user=request.user
        )

        context = {
            "bool": True,
            "wishlist_count": WishList.objects.filter(user=request.user).count()  # Updated count
        }

    return JsonResponse(context)

from django.core.exceptions import ObjectDoesNotExist

@login_required  
def remove_wishlist(request):
    pid = request.GET.get('id')  # Use get() to avoid KeyError if 'id' is not in GET
    try:
        # Attempt to retrieve the wishlist item
        wishlist_item = WishList.objects.get(id=pid, user=request.user)
        wishlist_item.delete()

        # Recalculate wishlist count after deletion
        wishlist = WishList.objects.filter(user=request.user)
        wishlist_count = wishlist.count()

        context = {
            "bool": True,
            "wishlist": wishlist,
        }
        
        wishlist_json = serializers.serialize('json', wishlist)
        data = render_to_string("Core/async/remove_wishlist.html", context)
        
        return JsonResponse({"data": data, "wishlist_count": wishlist_count, "wishlist": wishlist_json})

    except ObjectDoesNotExist:
        # Handle the case where the wishlist item does not exist
        return JsonResponse({"error": "Wishlist item does not exist."}, status=404)



def contact(request):
    return render(request, "Core/contact.html")

def ajax_contact(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']


    contact = Contact.objects.create(
        full_name = full_name,
        email = email,
        phone = phone,
        subject = subject,
        message = message,
    )

    data = {
        "bool": True,
        "message": "Message sent Successfully"
    }

    return JsonResponse({"data": data})


def faq(request):
    return render(request, "Settings/faq.html")

def policy_privacy(request):
    return render(request, "Settings/policy_privacy.html")

def why(request):
    return render(request, "Settings/Why_sellonEmariStore.html")

def return_policy(request):
    return render(request, "Settings/return_policy.html")
