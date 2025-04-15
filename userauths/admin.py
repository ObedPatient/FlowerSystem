from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Profile, Contact, AdminRevenueRecord

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

#class ProfileAdmin(admin.ModelAdmin):
 #   list_display = ['user','full_name','profile_image','bio','phone']
 
 

class RevenueRecordAdmin(admin.ModelAdmin):
    list_display = ('adminUser', 'total_revenue', 'monthly_revenue')
    ordering = ['-created_at']

class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name','email','subject']
    
admin.site.register(AdminRevenueRecord, RevenueRecordAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Profile)
admin.site.register(Contact, ContactAdmin)