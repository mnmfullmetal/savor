from django import forms

class ProductSearchForm(forms.Form):
    product_name = forms.CharField(max_length=60, required=False)
    barcode = forms.CharField(max_length=16, required=False)

    def clean(self):
        cleaned_data = super().clean()
        barcode = cleaned_data.get('barcode')
        product_name = cleaned_data.get('product_name')

        if not barcode and not product_name:
            raise forms.ValidationError("Please provide either a barcode or a product name.")

        if barcode:
            if not barcode.isdigit():
                self.add_error('barcode', "Barcode must contain only digits.")

        return cleaned_data


