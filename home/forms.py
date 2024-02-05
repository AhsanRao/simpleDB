from django import forms
from .models import Item, Person


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["asset_tag_number", "item_name", "serial_number", "install_date"]
        widgets = {
            "install_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "gender",
            "email",
            "role",
            "street",
            "city",
            "state",
            "zipcode",
            "country",
            "home_phone_number",
            "business_phone_number",
        ]
        widgets = {
            # Add widgets if you want to customize the form fields
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "zipcode": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "home_phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "business_phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }
