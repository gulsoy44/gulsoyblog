from django.contrib import admin
from .models import Post, Document

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1 # Number of empty forms to display for new documents

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'is_public')
    list_filter = ('is_public', 'author')
    search_fields = ('title', 'content')
    inlines = [DocumentInline] # Add Document forms directly in Post admin

    filter_horizontal = ('shared_with',) # Make ManyToManyField easier to manage