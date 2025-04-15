from django import forms
from .models import Vendor
from core.models import Product, Category, ProductImages, Category
from django_ckeditor_5.widgets import CKEditor5Widget
from django.forms import modelformset_factory, BaseModelFormSet
from taggit.forms import TagWidget  # Import the TagWidget from taggit
from django.core.exceptions import ValidationError
import re
from core.utils import convert_currency, get_exchange_rate
from decimal import Decimal






class AddProductForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter Product Title", "class": "form-control"}),
        required=True
    )
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        required=False
    )
    specifications = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        required=False
    )
    price = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "Sales Price", "class": "form-control"}),
        required=True
    )
    old_price = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "Old Price", "class": "form-control"}),
        required=True
    )
    in_stock = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "How Many are in Stock", "class": "form-control"}),
        required=True
    )
    mfd = forms.DateField(
        widget=forms.DateInput(attrs={"placeholder": "e.g: 22-11-02", "class": "form-control", "type": "date"}),
        required=True
    )
    digital = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control-file"}),
        required=True
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Select a category",
        required=True
    )
    currency = forms.ChoiceField(
        choices=[('RWF', 'RWF')],
        widget=forms.Select(attrs={"class": "form-control"}),
        initial='RWF',  # Default to RWF
        required=True
    )

    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'specifications',
            'price',
            'old_price',
            'in_stock',
            'mfd',
            'tags',
            'digital',
            'category',
            'currency'
        ]
        widgets = {
            'tags': TagWidget(attrs={'class': 'form-control', 'placeholder': 'Add tags'}),
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags:
            raise forms.ValidationError("This field is required.")
        return tags

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_old_price(self):
        old_price = self.cleaned_data.get('old_price')
        if old_price <= 0:
            raise forms.ValidationError("Old price must be greater than zero.")
        return old_price

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        old_price = cleaned_data.get('old_price')
        currency = cleaned_data.get('currency')

        if price and old_price and currency:
            if currency != 'RWF':
                # Fetch exchange rates with USD as base currency
                rates = get_exchange_rate(base_currency='USD')
                if not rates:
                    # Fallback rates in case API fails
                    fallback_rates = {
                        'USD': Decimal('1'),
                        'EUR': Decimal('1.08'),  # 1 USD = 0.925 EUR, so EUR to USD = 1/0.925
                        'GBP': Decimal('1.30'),  # 1 USD = 0.769 GBP, so GBP to USD = 1/0.769
                        'RWF': Decimal('1350'),  # 1 USD = 1350 RWF
                    }
                    rates = fallback_rates
                    print("Using fallback rates due to API failure.")

                # Convert prices to RWF
                converted_price = convert_currency(price, currency, 'RWF', rates)
                converted_old_price = convert_currency(old_price, currency, 'RWF', rates)

                if converted_price is None or converted_old_price is None:
                    raise ValidationError(
                        f"Unable to convert {currency} to RWF. Please try again later."
                    )

                cleaned_data['price'] = converted_price
                cleaned_data['old_price'] = converted_old_price

            # Always set currency to RWF after conversion
            cleaned_data['currency'] = 'RWF'

        return cleaned_data





class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ['id', 'images']  # Include 'id' if required by your model
        widgets = {
            'images': forms.FileInput(attrs={'class': 'form-control-file'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'].required = False



class BaseProductImageFormSet(BaseModelFormSet):
    def clean(self):
        """
        Add validation to check that at least one image is submitted.
        """
        super().clean()
        if any(self.errors):
            return

        # Check that at least one image is uploaded
        if not any(form.cleaned_data.get('images') for form in self.forms):
            raise forms.ValidationError('At least one image must be uploaded.')
        

# Create a formset using the custom base formset
ProductImageFormSet = modelformset_factory(
    ProductImages, 
    form=ProductImageForm, 
    formset=BaseProductImageFormSet, 
    extra=3,  # Allow 3 extra image upload forms by default
    can_delete=True  # Enable the ability to delete images
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['parent', 'title', 'image']
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Category Title'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

