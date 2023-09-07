import os
from django.conf import settings
from rest_framework import permissions, urls
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken import views
from django.views.generic import RedirectView
from .viewsets import router, ObtainAuthToken
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="REST API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   url='https://api.pnp.ifrn.edu.br/' if os.path.exists('/opt/pnp') else None,
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('api/doc/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/api/v1/login/', permanent=True)),
    path('api/v1/', include(router.urls)),
    path('api/v1/token/', ObtainAuthToken.as_view()),
] + static('/api/v1/media/', document_root=settings.MEDIA_ROOT) \
  + static('/api/v1/static/', document_root=settings.STATIC_ROOT)


