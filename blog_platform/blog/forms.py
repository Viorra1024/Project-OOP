from django import forms
from .models import Profile
from .models import Post, Category


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