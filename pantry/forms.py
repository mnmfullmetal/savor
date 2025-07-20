from django import forms

class ProductSearchForm():
    product_name = forms.CharField(max_length=60)
    bardcode = forms.CharField(max_length=16)

