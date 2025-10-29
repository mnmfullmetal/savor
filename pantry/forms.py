from django import forms

class ProductSearchForm(forms.Form):
    """
    Form for validating product search inputs.

    Requires either a barcode or a product name to be provided.
    """
    product_name = forms.CharField(max_length=60, required=False)
    barcode = forms.CharField(max_length=16, required=False)

    def clean(self):
        cleaned_data = super().clean()
        barcode = cleaned_data.get('barcode')
        product_name = cleaned_data.get('product_name')

        # ensure at least one search parameter is provided
        if not barcode and not product_name:
            raise forms.ValidationError("Please provide either a barcode or a product name.")

        # if a barcode is provided, validate that it contains only digits
        if barcode:
            if not barcode.isdigit():
                self.add_error('barcode', "Barcode must contain only digits.")

        return cleaned_data
