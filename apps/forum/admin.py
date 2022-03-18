from django.contrib import admin
from forum.models import Post

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'section', 'date')

admin.site.register(Post, PostAdmin)