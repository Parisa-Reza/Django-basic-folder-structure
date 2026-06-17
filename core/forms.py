from django import forms

class ProductSearchForm(forms.Form):
    product_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by product name...'
        })
    )