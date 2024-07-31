from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re


def validate_name(value):
    if not re.match(r'^[a-zA-Z ]+$', value):
        return False
    return True

def validate_username(value):
    if not re.match(r'^[a-zA-Z0-9 ]+$', value):
        return False
    return True

def validar_password(password1,password2):
    if("" in [password1,password2]):
        return "Todos los campos son obligatorios"
    if(password1!=password2):
        return "Las contraseñas no coinciden"
    if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$', password1):
        return "La contraseña debe tener al menos 8 caracteres, incluyendo números, letras mayúsculas y minúsculas, y caracteres especiales."
    return "OK"


def validar_correo(correo,if_existe=True):
    # Definir el patrón de la expresión regular para un correo electrónico válido
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # Usar re.match para verificar si el correo cumple con el patrón
    if re.match(patron, correo):
        if if_existe:
            if User.objects.filter(email=correo).exists():
                return False
        return True
    else:
        return False


class Login_Form(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Username',
                'aria-label':'Input group example',
                'aria-describedby':'basic-addon1',
                'style':'height:50px;',
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder':"Password",
            'aria-label':"Input group example",
            'aria-describedby':'basic-addon1',
            'style':"height:50px;",
        })
    )

class Register_Form(forms.Form):
    fname = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'First Name', 
                'aria-label':'Input group example',
                'aria-describedby':'basic-addon1',
                'style':'height:50px;',
            }
        )
    )
    lname = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'aria-label':'Input group example',
                'aria-describedby':'basic-addon1',
                'style':'height:50px;',
            }
        )
    )
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Username',
                'aria-label':'Input group example',
                'aria-describedby':'basic-addon1',
                'style':'height:50px;',
            }
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Email',
                'aria-label':'Input group example',
                'aria-describedby':'basic-addon1',
                'style':'height:50px;',
            }
        )
    )
    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Phone Number. Ej:+13552667535',
                'aria-label':'Input group example',
                'aria-describedby':'basic-addon1',
                'style':'height:50px;',
            }
        )
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder':"Password",
            'aria-label':"Input group example",
            'aria-describedby':'basic-addon1',
            'style':"height:50px;",
        })
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder':"Repeat Password",
            'aria-label':"Input group example",
            'aria-describedby':'basic-addon1',
            'style':"height:50px;",
        })
    )



class TwoFactorForm(forms.Form):
    num1 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg text-center px-0',
        'id': 'num1',
        'style': 'width: 38px;',
    }))
    num2 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg text-center px-0',
        'id': 'num2',
        'style': 'width: 38px;',
    }))
    num3 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg text-center px-0',
        'id': 'num3',
        'style': 'width: 38px;',
    }))
    num4 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg text-center px-0',
        'id': 'num4',
        'style': 'width: 38px;',
    }))
    num5 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg text-center px-0',
        'id': 'num5',
        'style': 'width: 38px;',
    }))
    num6 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg text-center px-0',
        'id': 'num6',
        'style': 'width: 38px;',
    }))


class ContactForm(forms.Form):
    fname = forms.CharField(
        label='First Name',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'First Name', 
            }
        )
    )
    lname = forms.CharField(
        label='Last Name',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 'placeholder': 'Last Name'
            }
        )
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Email', 
            }
        )
    )
    phone = forms.CharField(
        label='Phone',
        max_length=15,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Phone'
            }
        )
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control', 
                'placeholder': 'Message', 
            }
        )
    )

