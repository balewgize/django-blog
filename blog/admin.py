from django.contrib import admin

from accounts.models import Account
from .models import Category, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "author")
    list_filter = ("status", "last_update", "category")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "content")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}
