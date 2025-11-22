from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User
from .models import Profile

# ---------------- User Forms ---------------- #
class CustomUserCreationForm(forms.ModelForm):
    """Form for creating new users."""
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """Form for updating users (admin panel)."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "password", "is_active", "is_admin"]


class RegisterForm(CustomUserCreationForm):
    """User-facing register form (only email + password)."""
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "📧 Email",
            "class": "form-control"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "🔑 Password",
            "class": "form-control"
        })
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "bio", "avatar"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:ring focus:ring-indigo-200",
                "placeholder": "Enter your full name"
            }),
            "bio": forms.Textarea(attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:ring focus:ring-indigo-200",
                "placeholder": "Write something about yourself...",
                "rows": 4
            }),
            "avatar": forms.FileInput(attrs={
                "class": "w-full text-sm text-gray-600"
            }),
        }