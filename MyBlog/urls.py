# MyBlog/urls.py (Relevant sections for About and Contact)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from MyBlog import views as myblog_views # Renamed to avoid clash with app views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),     # User-related URLs
    path('blog/', include('posts.urls')),      # Post-related URLs

    # New static pages
    path('', myblog_views.HomePageView.as_view(), name='home'),
    path('about/', myblog_views.AboutPageView.as_view(), name='about'), # URL for About Us page
    path('contact/', myblog_views.ContactPageView.as_view(), name='contact'), # URL for Contact page
]

# ... (static and media files configuration) ...
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Not strictly needed for dev server, but good practice