from django.urls import path
from monitors import views

urlpatterns = [
    path('monitors/', views.monitor_list, name='monitor_list'),
    path('monitors/<int:pk>/', views.monitor_detail, name='monitor_detail'),
]