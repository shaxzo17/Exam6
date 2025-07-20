from django.contrib import admin
from .models import Post, Category, Comment , ContactMessage

class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'price', 'author')
    search_fields = ('name',)
    list_filter = ('created_at', 'category')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('text' ,)
    list_filter = ('created_at',)

admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(ContactMessage)