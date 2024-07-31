from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'login-username',
            'placeholder':"Enter your username"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'login-password',
            'placeholder':"Enter your password"
        })
    )


class Forget_pass_emailForm(forms.Form):
    email=forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class":"form-control",
            "id":"reminder-credential",
            "placeholder":"Enter your email"
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

class Restore_pass_form(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'login-password',
            'placeholder':"Enter your password"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'login-password',
            'placeholder':"Enter your password"
        })
    )
    