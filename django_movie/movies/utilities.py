from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Movie


def get_client_ip(request):
    """Определяем ip клиента"""

    X_FORWARDED_FOR = request.META.get('HTTP_X_FORWARDED_FOR')  # Получаем ip клиента из его хттп запроса
    if X_FORWARDED_FOR:  # Если айпи есть то
        ip = X_FORWARDED_FOR.split(',')[0]  # Мы просто убираем запятые и берем первый срез
    else:  # Иначе же
        ip = request.META.get('REMOTE_ADDR')  # Берем другой заголовок
    return ip


class MovieFilter(filters.FilterSet):
    """FilterSet - это класс, который позволяет поля по которым будет фильтрация и дополнительная логика к фильтрации
    в принципе, это же можно было сделать через гет запрос, но сделаем через дополнительный модуль"""

    class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
        """Тк мы будем искать в каком-то диапазоне ,а именно жанры, то, чтобы использовать в фильтрации слово in
        мы наследовали класс BaseInFilter, а класс CharFilter, чтобы искать жанры не по id, а по имени"""
        pass

    genres = CharFilterInFilter(field_name='genres__name', lookup_expr='in')
    # field_name - поле по которому будем искать, а lookup_expr - слово ,которое будем искользовать для фильтрации
    year = filters.RangeFilter()  # Чтобы искать в радиусе

    class Meta:
        model = Movie
        fields = ['genres', 'year']


class PaginationMovies(PageNumberPagination):
    page_size = 2  # Кол-во объектов на странице
    max_page_size = 100  # Максимальное кол-во загруженных объектов, то есть больше 100 не загрузит, даже если есть

    def get_paginated_response(self, data): # функция отвечает в каком виде будут выводится объекты пагинации
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'result': data
        })
