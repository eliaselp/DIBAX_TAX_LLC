from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        label='First Name',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': 'required'})
    )
    lname = forms.CharField(
        label='Last Name',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'required': 'required'})
    )
    phone = forms.CharField(
        label='Phone',
        max_length=15,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Phone'})
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message', 'required': 'required'})
    )
