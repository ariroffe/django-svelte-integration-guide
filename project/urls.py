from django.contrib import admin
from django.urls import path, include  # <-- changed

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('spa.urls')),  # <-- new
]
