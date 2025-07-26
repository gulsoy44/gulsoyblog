# MyBlog/MyBlog/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings') # <--- Ensure 'MyBlog.settings' is correct
application = get_wsgi_application()