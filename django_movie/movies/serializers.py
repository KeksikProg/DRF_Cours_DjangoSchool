from rest_framework import serializers

from .models import Movie, Review, Rating, Actor

'''Тут мы используем сериализаторы, это функции или классы, которые переделывают данные из типов питона в тип JSON
Это в принципе можно сделать и в просто django, но, тогда придется многие вещи писать ручками, 
такие как обращения к базе данных, сами сериализаторы, которые переделывают в json и много другое

Так же можно и наоборот, переделать данные в json, которые приходят со стороны клиента в питоновские типы данных 
и уже работать с ними'''


class ActorListSerializer(serializers.ModelSerializer):
    """Вывод актеров и режиссеров"""

    class Meta:
        model = Actor
        fields = ('id', 'name', 'image')


class ActorDetailSerializer(serializers.ModelSerializer):
    """Детальная информация по актерам"""

    class Meta:
        model = Actor
        fields = '__all__'


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""

    rating_user = serializers.BooleanField()
    middle_rating = serializers.IntegerField()

    class Meta:
        model = Movie  # Модель, которую мы хотим сериализовать
        fields = ('title', 'tagline', 'category', 'rating_user',
                  'middle_rating')  # Поля из модели, которые мы хотим сериализовать

        # По своей реализации, сериализаторы, очень сильно похожи на формы, так что так и можно их воспринимать


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзывов"""

    class Meta:
        model = Review
        fields = '__all__'


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр сериализатора, который будет откидывать детей из общего списка"""

    def to_representation(self, data):
        data = data.filter(parent=None)  # Просто заменяем обычную data на фильтрованную без детей
        return super().to_representation(data)  # И вызываем просто функцию, только с другой датой


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно отзывов"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        # Выше мы получаем родителя нашего отзыва, и через него получаем, всех детей то есть child -> parent -> childs
        # Не совсем понимаю функцию, но её можно и в другом месте использовать, в просто джанго
        return serializer.data


class ReviewListSerializer(serializers.ModelSerializer):
    """Вывод отзывов"""
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer  # Чтобы "дети" отзывов не выводились в общий список
        model = Review
        fields = ('name', 'text', 'children')


class MovieDetailSerializer(serializers.ModelSerializer):
    """Данные по одному фильму"""

    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    # Тут мы делаем, чтобы в json выводилось не id категории, а значение из поля модели(slug_field), ниже тоже самое
    directors = ActorListSerializer(read_only=True, many=True)
    # Тут ещё испольузется many потому что связь M2M и мы обрабатываем не один объект, а список
    actors = ActorListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    reviews = ReviewListSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ('draft',)


class CreateRatingSerializer(serializers.ModelSerializer):
    """Для создания или обновления рейтинга к фильму"""

    class Meta:  # Ну тут как обычно создаем
        model = Rating
        fields = ('star', 'movie')

    def create(self, validated_data):  # 2 параметр это уже прошедшая валидацию инфа, которая пришла от клиента
        # Ниже, тк нам возвращается кортеж из значений и True или False, то мы ненужную инфу именуем в _, чтобы не было ошибок
        rating, _ = Rating.objects.update_or_create(  # такой метод для того, чтобы один не мог проголосовать несколько раз
            ip=validated_data.get('ip'),  # Если есть такой ip в базе данных
            movie=validated_data.get('movie'),  # и такой фильм находится в базе данных
            defaults={'star': validated_data.get('star')}  # А тут, если выше нашлось и они связаны, то мы заменяем
            # в defaults мы передаем то, что должно быть изменено если было найдено или ,что должно быть создано в ином
            # И если айпи и фильм вместе, то мы просто обновляем звезду, если нет создаем
        )
        return rating
