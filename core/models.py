from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import Account
from Vendor.models import Vendor
from taggit.managers import TaggableManager 
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from core.utils import parse_datetime_safe
from django.db.models import Sum
from django.utils.timezone import now

from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.


STATUS_CHOICE = (
    ("processing","Processing"),
    ("out_for_delivery","Out for Delivery"),
    ("delivered","Delivered"),
)

STATUS = (
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("in_review","In Review"),
    ("rejected","Rejected"),
    ("published","Published"),
)

RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

from django.db import models
from django.utils.text import slugify

class Category(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    cid = ShortUUIDField(unique=True, length=10, prefix="cat", alphabet="abcdefgh1345")
    title = models.CharField(max_length=100)
    keyword = models.CharField(max_length=255, null=True, blank=True)
    desc = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)  # Ensure slug is unique
    image = models.ImageField(upload_to="category")

    class Meta:
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Auto-generate slug if not set
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent 
        return ' / '.join(full_path[::-1])

class Tags(models.Model):
    pass




class Product(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('RWF', 'Rwandan Franc'),
    ]

    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh1345")
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    
    title = models.CharField(max_length=1024, default='Nike Sneakers')
    slug = models.SlugField(max_length=1024, unique=True, blank=True)
    keyword = models.CharField(max_length=255, null=True, blank=True)
    desc = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path)
    description = CKEditor5Field('Text', config_name='extends', null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='RWF')

    specifications = CKEditor5Field('Text', config_name='extends', null=True, blank=True)
    tags = TaggableManager(blank=True)
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    status = models.BooleanField(default=True)
    in_stock = models.PositiveIntegerField()
    featured = models.BooleanField(default=False)
    mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix='sku', alphabet="abcdefgh1345")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        if self.old_price > 0:  # Prevent division by zero
            return (self.price / self.old_price) * 100
        return 0

    def save(self, *args, **kwargs):
        # Ensure slug is generated if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # Force currency to RWF when saving
        self.currency = 'RWF'

        super().save(*args, **kwargs)

class ProductImages(models.Model):
    images = models.ImageField(upload_to="product_images/")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,related_name="p_images")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"

####################################################################### Cart, Order, orderItem and address########################################


class CartOrder(models.Model):
    ORDER_TYPE_CHOICES = [
        ('online', 'Online'),
        ('in_store', 'In-Store'),
    ]
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cart_orders')
    customer = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_customer': True})
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='online')
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=3,default=settings.DEFAULT_CURRENCY)

    price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    traching_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_website_address = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=100, null=True, blank=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    sku = ShortUUIDField(null=True, length=4, prefix="SKU", max_length=10,alphabet="134567890")
    oid = ShortUUIDField(null=True, length=4, max_length=10,alphabet="134567890")

    stripe_payment_intent = models.CharField(max_length=1000, null=True, blank=True)


    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    total= models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def product_image(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))
    




####################################################################### Product Review, WishList, Address ########################################
####################################################################### Product Review, WishList, Address ########################################
####################################################################### Product Review, WishList, Address ########################################


class ProductReview(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,related_name='reviews')
    review = models.TextField(null=True, blank= True)
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title
    
    def get_rating(self):
        return self.rating
    

class WishList(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "WishLists"

    def __str__(self):
        return self.product.title
    


class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    address = models.CharField(max_length=100, null=True)
    mobile  = models.CharField(max_length=50)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Address'




class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=[('fixed', 'Fixed'), ('percentage', 'Percentage')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateTimeField(default='2024-01-01T00:00:00')
    usage_limit = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    def is_valid(self):
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False
        return True




class VendorOrder(models.Model):
    from core.models import CartOrder

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    cart_order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Vendor Orders"

    def __str__(self):
        return f"Vendor Order for {self.vendor} - {self.cart_order}"


