from django import forms
from core.models import ProductReview

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['review', 'rating']
        widgets = {
            'review': forms.Textarea(attrs={'placeholder': 'Write Review', 'class': 'form-control custom-textarea'}),
            'rating': forms.Select(attrs={'class': 'form-control custom-select'}),
        }
