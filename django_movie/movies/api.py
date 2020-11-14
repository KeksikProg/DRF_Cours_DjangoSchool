from django.db import models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Actor, Movie
from .serializers import ActorListSerializer, ActorDetailSerializer, MovieListSerializer, MovieDetailSerializer, \
    ReviewCreateSerializer, CreateRatingSerializer
from .utilities import MovieFilter, get_client_ip, PaginationMovies

"""
Помните я говорил, что с помощью generic классов мы упрощаем себе жизнь, делая меньше работы?
Ну так вот, есть способ с помощью, которого нам придется делть ещё меньше работы и это ViewSet-ы
Тут мы будем их записывать. Вообще, тут кому как хочется, и дженерик классы и вьюсеты пишутся не так долго,
тут скорее дело вкуса, написать всего 6 строк и 2 класса с помощью дженерик классов или же объеденить в один класс
под вьюсетами, и написать чуть больше строк, по правилам инкапусляции будет лучше использовать вьюсеты
"""


class ActorViewSet(viewsets.ViewSet):
    """Вывод списка актеров, так и отдельно одного"""

    @staticmethod
    def list(request):
        queryset = Actor.objects.all()
        serializer = ActorListSerializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def retrieve(request, pk=None):
        actor = get_object_or_404(Actor, pk=pk)
        serializer = ActorDetailSerializer(actor)
        return Response(serializer.data)


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод как списка фильмов, так и отдельно"""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter
    pagination_class = PaginationMovies

    def get_queryset(self):
        """Тут все осталось без изменений"""

        movies = Movie.objects.filter(draft=False).annotate(  # annotate это по сути тоже фильтрация
            rating_user=models.Count('ratings', filter=models.Q(ratings__ip=get_client_ip(self.request)))
            # rating_user это поле, которое мы придумали, но оно будет при выводе к каждому объекту модели Movie
            # Мы запрашиваем кол-во(count) объектов рейтинга с фильтром ip человека, а тк рейтинг к одному фильму
            # Можно поставить всего один раз, то у наc значение будет либо 0 либо 1, что равно True или False )
        ).annotate(
            middle_rating=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
            # Выше мы просто запрашиваем сумму(Sum) всех звезд и делим их на кол-во(Count) звезд
            # Это поле тоже не будет в базе данных, но оно будет при каждом объекте Movie при выводе
            # Метод F для того, чтобы с полученым значением можно было проводить математические вычесления
        )
        return movies
        # Так получаем список фильмов без черновика и допонительно с полем rating_user(Но этого поля в базе данных нет)
        # Сериализуем наш список с фильмами(Many, говорит о том, что у нас будет несколько записей, то есть список)

    def get_serializer_class(self):
        """Переназначаем метод, тк нам нужно, чтобы в разные моменты были разные сериализаторы"""

        if self.action == 'list':
            return MovieListSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer


class ReviewCreateViewSet(viewsets.ModelViewSet):
    """Создание отзывов к фильмам"""

    serializer_class = ReviewCreateSerializer


class AddStarRatingViewSet(viewsets.ModelViewSet):
    """Добавление рейтинга к фильмам"""

    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


"""
ViewSet - Корневой класс
ReadOnlyModelViewSet - класс, который позволяет только safe запросы делать(get) в основном для вывода списков или объект
ModelViewSet - класс, который позволяет использовать все запросы и для вывода может и для создания объектов 
"""