from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('wallet/', include('wallet.urls')),
    path('admin/', admin.site.urls),
]
