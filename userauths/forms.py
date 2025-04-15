from typing import Any, Dict
from django import forms
from .models import Account, Profile
from django import forms
from .models import Account  # Adjust the import according to your project structure
from django.core.exceptions import ValidationError
import re

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password',
        'class': 'form-control',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'

        # Apply the form-control class to all fields
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        # Modify phone_number widget to include the intl-tel-input class
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control intl-tel-input',
            'id': 'phone',  # Set the ID for JavaScript initialization if needed
        })

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.isalpha():
            raise ValidationError("First name should only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            raise ValidationError("Last name should only contain letters.")
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Ensure phone number only contains digits
            if not re.match(r'^\+?\d{10,15}$', phone_number):  # Adjust regex as needed
                raise ValidationError("Enter a valid phone number. It should contain 10 to 15 digits and may start with a '+' sign.")
        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Ensure password is at least 8 characters long
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            # Ensure password contains at least one digit
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one digit.")
            # Ensure password contains at least one uppercase letter
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_customer = True  # Mark the user as a customer
        if commit:
            user.save()
        return user



class VendorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password',
        'class': 'form-control',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

    def __init__(self, *args, **kwargs):
        super(VendorRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.isalpha():
            raise ValidationError("First name should only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            raise ValidationError("Last name should only contain letters.")
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Ensure phone number only contains digits
            if not re.match(r'^\+?\d{10,15}$', phone_number):  # Adjust regex as needed
                raise ValidationError("Enter a valid phone number. It should contain 10 to 15 digits and may start with a '+' sign.")
        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Ensure password is at least 8 characters long
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            # Ensure password contains at least one digit
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one digit.")
            # Ensure password contains at least one uppercase letter
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter.")
        return password

    def clean(self):
        cleaned_data = super(VendorRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_vendor = True  # Mark the user as a vendor
        if commit:
            user.save()
        return user

    


class ProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(widget=forms.ClearableFileInput(attrs={"placeholder": "PROFILE IMAGE"}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "FULL NAME"}))
    bio = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "BIOGRAPHY"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "PHONE"}))

    class Meta:
        model = Profile
        fields = ['profile_image', 'full_name', 'bio', 'phone']

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and not full_name.replace(" ", "").isalpha():
            raise ValidationError("Full name should only contain letters and spaces.")
        return full_name

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) > 500:  # Adjust the length as needed
            raise ValidationError("Bio cannot exceed 200 characters.")
        return bio

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Ensure phone number only contains digits, with optional '+' at the beginning
            if not re.match(r'^\+?\d{10,15}$', phone):  # Adjust regex as needed
                raise ValidationError("Enter a valid phone number. It should contain 10 to 15 digits and may start with a '+' sign.")
        return phone
