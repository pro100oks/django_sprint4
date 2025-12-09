from django.contrib import admin
from .models import Post, Category, Location, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'location',
        'is_published',
        'pub_date'
    )
    list_filter = (
        'is_published',
        'category',
        'location',
        'author'
    )
    search_fields = (
        'title',
        'text'
    )
    date_hierarchy = 'pub_date'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'is_published',
        'created_at'
    )
    prepopulated_fields = {
        'slug': ('title',)
    }
    search_fields = (
        'title',
        'description'
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'is_published',
        'created_at'
    )