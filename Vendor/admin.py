from django.contrib import admin
from .models import Vendor, Service
from django.utils.safestring import mark_safe


class VendorAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'vid', 'contact', 'joined_date', 'vendor_image', 'vendor_id_image', 'get_user')
    list_display_links = ('email',)  # Changed to tuple
    list_filter = ('joined_date',)

    # Fields to search through in the admin search bar
    search_fields = ('email', 'vid', 'contact')

    # Only use fieldsets for layout (remove `fields` to avoid conflicts)
    readonly_fields = ('vid', 'joined_date', 'vendor_image', 'vendor_id_image')

    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'email', 'contact')
        }),
        ('Identification', {
            'fields': ('vid', 'id_image', 'vendor_id_image')
        }),
        ('Additional Details', {
            'fields': ('address', 'description', 'image', 'vendor_image')
        }),
        ('Metadata', {
            'fields': ('joined_date',)
        }),
    )

    def get_user(self, obj):
        return obj.user.username if obj.user else 'No User'
    get_user.short_description = 'Associated User'

    def vendor_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return 'No Image'
    vendor_image.short_description = 'Profile Image'

    def vendor_id_image(self, obj):
        if obj.id_image:
            return mark_safe(f'<img src="{obj.id_image.url}" width="50" height="50" />')
        return 'No ID Image'
    vendor_id_image.short_description = 'ID Image'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)



class VendorService(admin.ModelAdmin):
    list_display = ['name','price','created_at']










# Register the model and custom admin
admin.site.register(Vendor,VendorAdmin)
admin.site.register(Service, VendorService)



