from django import forms
from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']


class OrderTrackingForm(forms.Form):
    order_id = forms.CharField(max_length=50, label='Enter Order ID')

