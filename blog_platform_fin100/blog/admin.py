from django.contrib import admin
from .models import Post, Comment, Category

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'created_at')  # Убираем поля, которых нет в модели
    search_fields = ('title', 'content')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'content', 'created_at')  # Убираем поля, которых нет в модели
    search_fields = ('content',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Убираем 'slug', так как его нет в модели
    search_fields = ('name',)

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)


