from core.models import Product, ProductImages, ProductReview, Vendor, CartOrder, CartOrderItem, Category, WishList, Address
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages
from django.db.models import Max, Min
from django.db.models import Count
from userauths.models import Profile

def default(request):
    categories = Category.objects.annotate(product_count=Count('category'))  # Count products for each category
    vendors = Vendor.objects.all()
    profile = Profile.objects.all()
    address = None  # Set a default value for the address
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))

    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(user=request.user)
        except Address.MultipleObjectsReturned:
            address = Address.objects.filter(user=request.user).first()
        except Address.DoesNotExist:
            pass

        wishlist_count = WishList.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0

    return {
        'categories': categories,
        'wishlist_count': wishlist_count,
        'address': address,
        'vendors': vendors,
        'min_max_price': min_max_price,
        'profile': profile
    }
