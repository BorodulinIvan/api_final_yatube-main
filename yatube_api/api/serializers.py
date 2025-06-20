from django.contrib.auth import get_user_model
from rest_framework import serializers
from posts.models import Follow, Post, Comment, Group, User


UserForSerializer = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserForSerializer
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = UserForSerializer.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ("user", "following")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "following"),
                message="Вы уже подписаны на этого пользователя.",
            )
        ]

    def validate(self, data):
        if data["user"] == data["following"]:
            raise serializers.ValidationError("Нельзя подписаться на самого себя.")
        return data


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False
    )
    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = ("id", "text", "pub_date", "author", "group", "image")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "post", "text", "created")


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "title", "slug", "description")
