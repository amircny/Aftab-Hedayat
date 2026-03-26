from django import forms
from django.contrib.auth import authenticate, get_user_model
User = get_user_model()

class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "input",
            "placeholder": "example@email.com"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "رمز عبور"
        })
    )

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError("Invalid email or password")

        if not user.is_verified:
            raise forms.ValidationError("Your account is not verified. Check your email.")

        cleaned["user"] = user
        return cleaned
#......................................................................................................    
class TeacherEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]    