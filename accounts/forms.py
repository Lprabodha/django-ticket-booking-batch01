from django import forms
from django.contrib.auth import get_user_model


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label="User Name")
    email = forms.EmailField(max_length=254, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError("Username Already Exits")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip() #  test@gamil.com -> 
        normalized_email = get_user_model().objects.normalize_email(email) # TEST@GMAIL.COM -> test@gamil.com
        
        if get_user_model().objects.filter(email__iexact=normalized_email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        
        return normalized_email 
    
    def save(self):
        return get_user_model().objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"]
        )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Password do not match")
        
        return cleaned_data
    
class LoginForm(forms.Form):
    identifier = forms.CharField(max_length=254, label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password") # 124555 -> ......
