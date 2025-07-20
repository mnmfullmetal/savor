from django import forms

class ProductSearchForm(forms.Form):
    product_name = forms.CharField(max_length=60, required=False)
    barcode = forms.CharField(max_length=16, required=False)

