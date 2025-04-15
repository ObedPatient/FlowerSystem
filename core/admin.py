from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from core.models import Product, Coupon,ProductImages,ProductReview, CartOrder, CartOrderItem, Category, WishList, Address, VendorOrder

# Register your models here.

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['user','title','product_image','category','price','featured','product_status']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','category_image']



class CategoryAdmin2(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'


class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status']
    list_display = ['user','price','paid_status','order_date','payment_method','product_status']

class CartOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order','invoice_no', 'item','image', 'qty', 'price','total']


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user','product', 'rating','review']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user','product','date']

class AddressAdmin(admin.ModelAdmin):
    list_editable = ['address','status']
    list_display = ['user','address','mobile','status']

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'expiry_date', 'usage_limit')
    list_filter = ('discount_type', 'expiry_date')
    search_fields = ['code', 'vendor__email']

    def save_model(self, request, obj, form, change):
        # If a vendor is logged in, assign the coupon to the vendor
        if request.user.groups.filter(name='Vendors').exists():
            obj.vendor = request.user
        super().save_model(request, obj, form, change)



admin.site.register(Product, ProductAdmin)
admin.site.register(CartOrder,CartOrderAdmin)
admin.site.register(Category, CategoryAdmin2)
admin.site.register(CartOrderItem,CartOrderItemAdmin)
#admin.site.register(ProductImages, ProductImagesAdmin)
admin.site.register(ProductReview,ProductReviewAdmin)
admin.site.register(WishList,WishlistAdmin)
admin.site.register(Address,AddressAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(VendorOrder)
