from django import forms
from .models import Profile
from .models import Post, Category


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']


class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="Без категории")

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category']