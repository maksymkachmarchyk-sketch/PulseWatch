from django.urls import path

from checks import views

urlpatterns = [
    path('api/monitors/<int:monitor_id>/history/',views.check_history, name="check_history"),
]