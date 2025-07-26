from django.db import models
from django.conf import settings # Import settings to reference AUTH_USER_MODEL
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='private_posts', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

class Document(models.Model):
    post = models.ForeignKey(Post, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_documents/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.file.name.split("/")[-1]} for {self.post.title}'