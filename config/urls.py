"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from config import settings
from config.flask_app import generate_audio_feedback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.account.urls')),
    # MAIN
    path('', include('apps.rayhan.homePage.urls')),
    path('waitress/', include('apps.rayhan.waitressPage.urls')),
    # MEAL
    path('meal/', include('apps.rayhan.mealList.urls')),
    # KITCHEN
    path('kitchen/', include('apps.rayhan.kitchen.urls')),

    # BREAD WAITRESS
    path('bread/', include('apps.rayhan.bread.urls')),

    # REPORT
    path('report/', include('apps.rayhan.report.urls')),

    # REPORT
    path('meat/', include('apps.rayhan.meat.urls')),
    path('meat/', include('apps.rayhan.meat.urls')),

    path('generate-feedback/<str:task_type>/', generate_audio_feedback, name='generate_feedback'),

    # REPORT
    path('samsa/', include('apps.rayhan.samsa_kebab.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

