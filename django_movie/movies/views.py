from django.db import models
from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Actor
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewCreateSerializer, CreateRatingSerializer, \
    ActorListSerializer, ActorDetailSerializer
from .utilities import get_client_ip, MovieFilter
from django_filters.rest_framework import DjangoFilterBackend


class MovieListView(ListAPIView):
    # APIView это главный класс в drf, от него наследуются все остальные класcы, а он от класса django 'View'
    # Раньше мы использовали класс APIView, но теперь используем generic class ListAPIView, он удобнее
    """Вывод списка фильмов"""

    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend,) # Тут мы обозначили, что будет использоваться для фильтрации этих записей
    filterset_class = MovieFilter # Класс по которому будем фильтровать

    permission_classes = [permissions.IsAuthenticated] # Мы сделали, чтобы список могли получить, только аутентиф. юзеры
    # Этот атрибут, говорит о том, какие должны быть у пользователя права доступа для контента

    def get_queryset(self):
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


class MovieDetailView(RetrieveAPIView):
    """Вывод под одному фильму"""

    queryset = Movie.objects.filter(draft=False)
    serializer_class = MovieDetailSerializer


class ReviewCreateView(CreateAPIView):
    """Добавлние отзывов"""
    serializer_class = ReviewCreateSerializer
    # В оправдание дженерик классов, в данном случае это очень удобно, мы заменяем целый метод пост на одну строку, так
    # ещё на страницу с созданием добавляется удобная форма


class AddStarRatingView(CreateAPIView):
    """Добавление рейтинга к фильму"""

    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        """Тк нам надо добавлять ip в модель, то мы используем функцию,
        которая будет добавлять параметры, которые мы указали, при сохранении"""

        serializer.save(ip = get_client_ip(self.request))


    # def post(self, request):
    #     """Делаем с помощью пост запроса рейтинг фильму"""
    #
    #     serializer = CreateRatingSerializer(data=request.data)  # Сериализируем данные полученные от пользователя
    #     if serializer.is_valid():  # Если они верны
    #         serializer.save(ip=get_client_ip(request))  # То сохраняем данные попутно добавляя ip адресс
    #         return Response(status=201)  # И возвращаем код 201 (CREATE)
    #     else:
    #         return Response(status=400)  # Если же все прошло хуже, то возвращаем код 400 (BAD REQUEST)


class ActorListView(ListAPIView):
    """Вывод списка актеров и режиссеров"""

    """Тут мы будем использовать generic классы, это те классы, которые требуют от нас даже меньше, чем обычное view, 
    мы просто казываем модель и сериализатор, а дальше класс сам делает
    в данном случае класс сам выведет список"""

    """И в итоге, что у нас вышло, 3 строчки в сериализаторе и 2 строчки тут, не считая комментарии"""
    queryset = Actor.objects.all()  # просто все наши объекты из модели Actor
    serializer_class = ActorListSerializer  # Сериализер с помощью которого мы будем передавать данные


class ActorDetailView(RetrieveAPIView):
    """Для детального вывода актера или режиссера"""

    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer

"""
ListAPIView - для вывода списка  
RetrieveAPIView - для вывода одной записи
CreateAPIView - для создания записей
"""