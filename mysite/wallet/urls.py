from django.urls import path

from . import views

app_name = 'wallet'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('<int:wallet_id>/', views.detail, name='detail'),
    path('<int:wallet_id>/send/', views.send, name='send'),
]
