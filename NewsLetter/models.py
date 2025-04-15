from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.

class Subscriber(models.Model):
    email = models.EmailField(unique=True)


    def __str__(self):
        return self.email 
    

class EmailTemplate(models.Model):
    subject = models.CharField(max_length=255)
    message = CKEditor5Field('Text', config_name='extends', null=True, blank=True)
    recipients = models.ManyToManyField(Subscriber, related_name='email_templates')

    def __str__(self):
        return self.subject 
    


class UserDeviceInfo(models.Model):
    username = models.CharField(max_length=150, default='Anonymous')  # Add this field
    ip_address = models.GenericIPAddressField()
    browser_info = models.TextField()
    timezone = models.CharField(max_length=100, blank=True, null=True)
    cookies = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.browser_info}"

