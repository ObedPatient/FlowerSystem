from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import VendorOrder, CartOrder
from django.db import transaction
from userauths.models import AdminRevenueRecord
from decimal import Decimal
from decimal import InvalidOperation

@receiver(post_save, sender=VendorOrder)
def update_vendor_total(sender, instance, **kwargs):
    print(f"VendorOrder signal triggered for Vendor: {instance.vendor.title}")
    transaction.on_commit(lambda: instance.vendor.update_total_earnings())
    


@receiver(post_save, sender=CartOrder)
def update_admin_revenue_on_order(sender, instance, created, **kwargs):
    """Update the admin revenue when a paid order is created or updated."""
    
    # Only proceed if the order is paid
    if instance.paid_status:
        print(f"Order {instance.id} is paid. Updating admin revenue...")

        # Get or create the AdminRevenueRecord for the admin user
        admin_revenue, _ = AdminRevenueRecord.objects.get_or_create(
            adminUser=instance.user  # Adjust to the appropriate admin account
        )

        # Convert price to Decimal safely
        try:
            price = Decimal(str(instance.price))  # Ensure safe conversion from float or string
        except (ValueError, TypeError, InvalidOperation):
            print(f"Invalid value for instance.price: {instance.price}")
            return
        
        # Ensure total_revenue and monthly_revenue are Decimal before performing addition
        try:
            admin_revenue.total_revenue = Decimal(str(admin_revenue.total_revenue)) + price
            admin_revenue.monthly_revenue = Decimal(str(admin_revenue.monthly_revenue)) + price
        except (ValueError, TypeError, InvalidOperation):
            print(f"Invalid value for total_revenue or monthly_revenue: {admin_revenue.total_revenue}, {admin_revenue.monthly_revenue}")
            return

        # Save the updated values
        admin_revenue.save(update_fields=['total_revenue', 'monthly_revenue'])

        # Convert Decimal to string for printing
        print(f"Admin revenue updated: {admin_revenue.total_revenue}")
