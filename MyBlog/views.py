# MyBlog/views.py

from django.views.generic import TemplateView, ListView
from posts.models import Post # Import the Post model from the 'posts' app
from django.db import models # Import models for Q objects if needed in future, good practice

class HomePageView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'public_posts'
    ordering = ['-date_posted']

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_public=True)
        # --- ADD THESE PRINT STATEMENTS ---
        print("\n--- DEBUG: HomePageView Queryset ---")
        print(f"Number of public posts found in DB: {queryset.count()}")
        if queryset.exists():
            print("Public post titles:")
            for post in queryset:
                print(f"  - '{post.title}' (ID: {post.pk}, Is Public: {post.is_public})")
        else:
            print("No public posts retrieved by the queryset.")
        print("--- END DEBUG ---\n")
        # -----------------------------------
        return queryset

class AboutPageView(TemplateView):
    """
    Renders the static 'About Us' page.
    - Uses TemplateView for simple static page rendering.
    - `template_name`: Points to the 'about.html' template.
    """
    template_name = 'about.html'

class ContactPageView(TemplateView):
    """
    Renders the static 'Contact' page.
    - Uses TemplateView for simple static page rendering.
    - `template_name`: Points to the 'contact.html' template.
    """
    template_name = 'contact.html'