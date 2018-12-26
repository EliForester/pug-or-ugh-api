from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = get_user_model()


class UserDogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserDog
        fields = ('status',)

    def create(self, validated_data):
        try:
            userdog, created = models.UserDog.objects.create(**validated_data)
        except IntegrityError:
            userdog = models.UserDog.objects.get(user=validated_data['user'],
                                                 dog=validated_data['dog'])
            userdog.status = validated_data['status']
            userdog.save()
        return userdog


class DogSerializer(serializers.ModelSerializer):
    status = UserDogSerializer(required=False,
                               many=True,
                               read_only=False)

    class Meta:
        fields = (
            'id',
            'name',
            'image_filename',
            'breed',
            'age',
            'gender',
            'size',
            'status',
        )
        model = models.Dog


class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('user',)
        model = models.UserPref
        user = get_user_model()

    def create(self, validated_data):
        try:
            userpref = models.UserPref.objects.create(**validated_data)
        except IntegrityError:
            userpref = models.UserPref.objects.get(user=validated_data['user'])
            userpref.age = validated_data['age']
            userpref.gender = validated_data['gender']
            userpref.size = validated_data['size']
            userpref.save()
        return userpref
