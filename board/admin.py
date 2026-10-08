from django.contrib import admin

from .models import Category, Post, Response


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('headline', 'author', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('headline', 'body', 'author__email')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('post__headline', 'author__email', 'body')
