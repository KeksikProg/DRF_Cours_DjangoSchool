from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views, api

urlpatterns = format_suffix_patterns([  # Данный список для того, чтобы для нескольких урл использовать один класс
    path('movie/', api.MovieViewSet.as_view({'get': 'list'})),
    path('movie/<int:pk>/', api.MovieViewSet.as_view({'get': 'retrieve'})),
    path('review/', api.ReviewCreateViewSet.as_view({'post': 'create'})),
    path('rating/', api.AddStarRatingViewSet.as_view({'post': 'create'})),
    path('actors/', api.ActorViewSet.as_view({'get': 'list'})),  # Ключ это HTTP метод, знач. это метод класса вьюсета
    path('actors/<int:pk>', api.ActorViewSet.as_view({'get': 'retrieve'})),
])
