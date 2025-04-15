from django.db import models
from userauths.models import Account
from django.utils.html import mark_safe
from shortuuid.django_fields import ShortUUIDField
from django.db.models import Sum

def user_directory_path(instance, filename):
    # Define the path where vendor images and documents will be uploaded
    return 'vendor_files/{0}/{1}'.format(instance.vid, filename)


class Vendor(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)  # Changed to User; adjust if Account
    vid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh1345")
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)  # Profile image
    id_image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)  # New field for ID image
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=100, default='28 St Avenue')
    contact = models.CharField(max_length=15, default='+250784958773')
    email = models.EmailField(max_length=254, unique=True)
    joined_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Sellers"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def vendor_logo(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.id_image.url))

    def __str__(self):
        return self.user.username if self.user else 'No User'           
    



class Service(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



