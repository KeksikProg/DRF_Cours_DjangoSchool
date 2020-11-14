from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # Для админки рест фреймворк
    path('ckeditor/', include('ckeditor_uploader.urls')),  # для скедитора
    path('api/', include(('movies.urls', 'movies'), namespace='movies')),  # Наше приложение собственное
    path('auth/', include('rest_framework_social_oauth2.urls')),  # для регистрации через соц. сети
    path('auth/', include('djoser.urls.authtoken')),  # для создания токенов
    path('auth/', include('djoser.urls.jwt')),  # для жвт токенов
    path('auth/', include('djoser.urls')),  # для остальных действий по регистрации, аутентефикации и тд
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
auth/users/ - для создания пользователей (передаем username,password,email в JSON)
auth/token/login/ - для аутентификации (получаем token)
auth/token/logout/ - для выхода (передаем токен в headers)

у auth/users/ - есть ещё урлы, так что это не только созданию юзера, ещё и активация,смена пароля, и куча других методов
все методы указаны в djoser/views.py в классе UserViewSet
"""
