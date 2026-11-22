"""
URL configuration for PulseWatch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path, include
from django.views.static import serve

FRONTEND_DIR = settings.BASE_DIR.parent / 'frontend'


def frontend(request, path=''):
    path = path.strip('/')
    if not path or (FRONTEND_DIR / path).is_dir():
        path = f'{path}/index.html'.lstrip('/')
    return serve(request, path, document_root=FRONTEND_DIR)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('monitors.urls')),
    path('', include('checks.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/incidents/', include('incidents.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    re_path(r'^(?P<path>.*)$', frontend),  # must stay last
]
