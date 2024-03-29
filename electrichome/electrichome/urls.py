"""
URL configuration for electrichome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import my_view, geocode

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', my_view, name='my_view'),
    path('api/geocode/<str:city>/<str:state>/', geocode, name='geocode'),
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # # Needed during deployment, not development