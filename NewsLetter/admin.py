from django.contrib import admin
from .models import Subscriber, EmailTemplate, UserDeviceInfo
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django_ckeditor_5.widgets import CKEditor5Widget  # Import the correct widget

# Register your models here.

# Define the custom form for the EmailTemplate admin
class EmailTemplateAdminForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        widgets = {
            'message': CKEditor5Widget(),  # Use the CKEditor5Widget for rich text editing
        }

class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateAdminForm

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # After the many-to-many relationship has been saved
        obj = form.instance
        print(f"Recipients After Saving: {list(obj.recipients.all())}")  # Debug statement to check recipients

        recipients = [subscriber.email for subscriber in obj.recipients.all()]
        print(f"Processed Recipients: {recipients}")

        if not recipients:
            print("Warning: No recipients found. Email will not be sent.")
            return

        # Send the email if recipients are found
        from_email = settings.EMAIL_HOST_USER
        subject = obj.subject
        html_message = obj.message

        # Send the email
        send_mail(
            subject,
            "",  # Leave the plain text empty if using `html_message`
            from_email,
            recipients,
            fail_silently=False,
            html_message=html_message
        )
        print("Email sent successfully.")



class UserDeviceInfoAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'browser_info', 'timezone', 'created_at')

# Register the models in the Django admin
admin.site.register(Subscriber)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(UserDeviceInfo,UserDeviceInfoAdmin)
