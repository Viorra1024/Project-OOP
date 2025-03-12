from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from .models import Profile, Post, Category

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),  # Все доступные категории
        required=False,
        empty_label="Выберите категорию"
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category']  # Теперь категория будет доступна при создании

# 🔹 Добавляем форму регистрации с проверкой пароля
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Введите вашу электронную почту.",  # 🛠 Изменяем стандартный текст
            "invalid": "Введите корректный email-адрес."
        }
    )
    username = forms.CharField(
        max_length=150,
        error_messages={
            "required": "Введите имя пользователя.",
            "unique": "Пользователь с таким именем уже существует."
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            "required": "Введите пароль.",
            "min_length": "Пароль должен содержать не менее 8 символов."
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            "required": "Повторите пароль.",
            "invalid": "Пароли не совпадают."
        }
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        try:
            validate_password(password)  # 🔹 Проверка пароля Django
        except forms.ValidationError as e:
            raise forms.ValidationError("Пароль слишком простой или небезопасный.")  # 🛠 Кастомный текст ошибки
        return password

