from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.fields import HiddenField
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, \
    TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        lookup_field = 'slug'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        lookup_field = 'slug'
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class ListTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )

    class Meta:
        fields = '__all__'
        model = Review

    def ReviewValidation(self):
        title_id = self.kwargs.get('id')
        title = get_object_or_404(Title, pk=title_id)
        reviews = self.request.user.reviews
        if reviews.filter(title).exists:
            raise serializers.ValidationError(
                msg='Вы уже оставляли обзор на данное произведение',
                status=status.HTTP_400_BAD_REQUEST
            )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='text'
    )

    class Meta:
        fields = '__all__'
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def validate_email(self, attrs):
        if attrs == self.context['request'].user:
            raise serializers.ValidationError(
                'Такой email уже зарегистрирован!')
        return attrs

    # проверка на изменение роли если не Админ
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.email)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.email)
        instance.last_name = validated_data.get('last_name', instance.content)
        instance.bio = validated_data.get('bio', instance.created)
        is_superuser = self.user.is_superuser
        if not is_superuser:
            raise serializers.ValidationError('Роль юзера менять нельзя!')
        instance.role = validated_data.get('role', instance.created)
        instance.confirmation_code = validated_data.get('email',
                                                        instance.confirmation_code)
        instance.save()
        return instance

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email')


class TokenSerializer(TokenObtainPairSerializer, TokenObtainSerializer):
    token_class = RefreshToken

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields["password"] = HiddenField(default='')

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        return token

    def validate(self, attrs):
        user = get_object_or_404(User, username='username')
        if user['username'] == attrs['username']:
            raise serializers.ValidationError('Юзер не зарегестрирован!')
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["access"] = str(refresh.access_token)
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return {'token': data}
