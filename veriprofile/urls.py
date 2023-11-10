from django.contrib import admin
from django.urls import include,path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('app.urls')),
    path('admin/', include('customadmin.urls')),
    path('dj-admin/', admin.site.urls),
    path("accounts/",include("django.contrib.auth.urls")),
    path("social_auth/",include("social_django.urls" , namespace = 'social'))
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
