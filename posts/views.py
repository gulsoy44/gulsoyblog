# posts/views.py

import os
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse # Import HttpResponse for file serving
from django.db import models # Import models for Q objects

from .models import Post, Document
from .forms import PostForm, DocumentFormSet

class PostListView(LoginRequiredMixin, ListView):
    """
    Displays a list of blog posts.
    - Requires user to be logged in (LoginRequiredMixin).
    - Orders posts by date_posted in descending order (newest first).
    - Filters posts based on user permissions:
        - Superusers see all posts.
        - Regular users see public posts and private posts explicitly shared with them.
    """
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            # Superusers (admins) can see all posts, regardless of public/private status
            return queryset
        else:
            # Regular users see public posts OR private posts they are shared with.
            # .distinct() is used to prevent duplicate posts if a post is both public
            # and shared with the user (though typically a post is one or the other).
            return queryset.filter(
                models.Q(is_public=True) | models.Q(shared_with=self.request.user)
            ).distinct()

class PostDetailView(UserPassesTestMixin, DetailView): # LoginRequiredMixin REMOVED
    """
    Displays the details of a single blog post.
    - Uses UserPassesTestMixin to enforce viewing permissions:
      - Public posts are viewable by all users (logged-in or not).
      - Private posts are viewable only by the author, users explicitly shared with, or superusers.
    - Redirects with an error message if the user does not have permission.
    """
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def test_func(self):
        post = self.get_object()
        # Check if the post is public (accessible to anyone)
        if post.is_public:
            return True
        # For private posts, check if the current user has permission
        # Only proceed with these checks if the user is authenticated
        elif self.request.user.is_authenticated:
            if self.request.user == post.author:
                return True
            elif self.request.user in post.shared_with.all():
                return True
            elif self.request.user.is_superuser:
                return True
        # If not public and not authenticated/authorized, deny access
        return False

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view this post.")
        # If the user is not authenticated, redirect to login for private posts.
        # Otherwise, if authenticated but unauthorized, redirect to the post list.
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('post-list') # Redirect to the post list if authenticated but no permission

class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Handles the creation of new blog posts.
    - Requires user to be logged in (LoginRequiredMixin).
    - Crucially, uses UserPassesTestMixin to ensure ONLY staff users (admins) can create posts.
    - Handles both Post form and Document formset for multiple file uploads.
    - Uses a database transaction to ensure atomicity (either post and documents are saved, or none are).
    - Redirects with an error message if a non-staff user tries to access.
    """
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        # Only staff users (who can access the admin site) can create posts
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to create posts.")
        return redirect('post-list') # Redirect to the post list or another appropriate page

    def get_form_kwargs(self):
        # Pass the current user to the PostForm to exclude them from 'shared_with' queryset
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        # Populate the document formset for handling file uploads
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['document_formset'] = DocumentFormSet(self.request.POST, self.request.FILES)
        else:
            data['document_formset'] = DocumentFormSet()
        return data

    def form_valid(self, form):
        # Set the author of the post to the current logged-in user
        form.instance.author = self.request.user
        context = self.get_context_data()
        document_formset = context['document_formset']

        # Use a transaction to ensure both post and documents are saved successfully
        with transaction.atomic():
            self.object = form.save() # Save the Post instance first
            if document_formset.is_valid():
                document_formset.instance = self.object # Link documents to the newly created post
                document_formset.save() # Save the documents
            else:
                # If document formset is invalid, prevent post creation and re-render with errors
                return self.form_invalid(form)

        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Handles updating existing blog posts.
    - Requires user to be logged in (LoginRequiredMixin).
    - Only the author of the post or a superuser can update it.
    - Handles both Post form and Document formset for updating/deleting files.
    - Uses a database transaction for atomicity.
    """
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def get_form_kwargs(self):
        # Pass the current user to the PostForm to exclude them from 'shared_with' queryset
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        # Populate the document formset with existing documents for the post
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['document_formset'] = DocumentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['document_formset'] = DocumentFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        document_formset = context['document_formset']

        with transaction.atomic():
            self.object = form.save() # Save the updated Post instance
            if document_formset.is_valid():
                document_formset.instance = self.object # Ensure documents are linked to this post
                document_formset.save() # Save (create/update/delete) documents
            else:
                # If document formset is invalid, prevent post update and re-render with errors
                return self.form_invalid(form)

        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        # Only the author or a superuser can update the post
        return self.request.user == post.author or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to edit this post.")
        return redirect('post-detail', pk=self.kwargs['pk'])

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Handles deletion of blog posts.
    - Requires user to be logged in (LoginRequiredMixin).
    - Only the author of the post or a superuser can delete it.
    - Redirects to the post list after successful deletion.
    """
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        # Only the author or a superuser can delete the post
        return self.request.user == post.author or self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Post deleted successfully!')
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to delete this post.")
        return redirect('post-detail', pk=self.kwargs['pk'])

def download_document(request, pk):
    """
    Allows authenticated and authorized users to download attached documents.
    - Retrieves the Document object by its primary key.
    - Checks if the user has permission to view the associated Post (same logic as PostDetailView).
    - If authorized, serves the file as an octet-stream.
    - Redirects with an error message if permissions are insufficient or file not found.
    """
    document = get_object_or_404(Document, pk=pk)
    post = document.post

    # Ensure user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to download documents.")
        return redirect('login')

    # Check permissions to view the associated post (and thus download its documents)
    if not (post.is_public or request.user == post.author or request.user in post.shared_with.all() or request.user.is_superuser):
        messages.error(request, "You do not have permission to download this document.")
        return redirect('post-detail', pk=post.pk)

    # Serve the file if permissions are met
    file_path = document.file.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    messages.error(request, "File not found.")
    return redirect('post-detail', pk=post.pk)
