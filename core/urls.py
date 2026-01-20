from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('turnos.urls')), # <--- ¡ESTO ES VITAL!
]