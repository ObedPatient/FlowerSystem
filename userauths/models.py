from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.html import mark_safe
from django.db.models.signals import post_save

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        from Vendor.models import Vendor
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        
        
         # Create an AdminRevenueRecord only if the user is a superuser
        if user.is_superadmin:
            AdminRevenueRecord.objects.create(adminUser=user)

        return user

class Account(AbstractBaseUser, PermissionsMixin):
    

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class Profile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="image", null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    verified = models.BooleanField(default=False)

    def image_tag(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return mark_safe(f'<img src="{self.profile_image.url}" width="50" height="50" />')
        return mark_safe('<img src="/static/assets/images/banner/default-profile.jpg" width="50" height="50" />')  # Default image

    def __str__(self):
        return self.user.username
    

class Contact(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Set default profile image and populate other fields
        default_image_path = 'default/user.png'  # Ensure this image exists in your media directory
        Profile.objects.create(
            user=instance,
            profile_image=default_image_path,
            full_name=f'{instance.first_name} {instance.last_name}',
            email=instance.email,
            phone=instance.phone_number,
            # Populate other fields as needed
        )

post_save.connect(create_user_profile, sender=Account)


class AdminRevenueRecord(models.Model):
    adminUser = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='admin_revenue')
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    monthly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revenue Record for {self.adminUser.username}"
