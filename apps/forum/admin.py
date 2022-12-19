from django.contrib import admin
from forum.models import Post, Section, Subsection

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'section', 'subsection', 'date')

admin.site.register(Post, PostAdmin)
admin.site.register(Section)
admin.site.register(Subsection)