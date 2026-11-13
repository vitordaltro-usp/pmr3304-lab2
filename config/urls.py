from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Login e logout nativos do Django (django.contrib.auth).
    path('contas/', include('django.contrib.auth.urls')),
    path('', include('blog.urls')),
]
