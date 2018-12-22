from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404, Http404, HttpResponse
from functools import reduce
from . import models
import operator
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

from . import serializers

valid_liked_statuses = {'liked': 'l', 'disliked': 'd', 'undecided': None}


def is_liked(liked_status):
    try:
        return valid_liked_statuses[liked_status]
    except KeyError:
        raise Http404


def reverse_liked(value):
    for key in valid_liked_statuses:
        if valid_liked_statuses[key] == value:
            return key


def map_age_to_q(ages):
    ages = ages.split(',')
    age_range_map = {'b': [0, 6], 'y': [7, 23], 'a': [24, 70], 's': [71, 360]}
    age_ranges = [age_range_map[x] for x in ages]
    q_list = []
    for age_range in age_ranges:
        q_list.append(reduce(operator.and_,
                             [Q(age__gte=age_range[0]),
                              Q(age__lte=age_range[1])]))
    return reduce(operator.or_, q_list)


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class DogView(RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        queryset = models.Dog.objects.all()
        liked_status = is_liked(self.kwargs['liked_status'])
        try:
            userpref = models.UserPref.objects.get(
                user=self.request.user)
            queryset = queryset.filter(
                gender__in=userpref.gender.split(','),
                size__in=userpref.size.split(',')
            )
            if userpref.age:
                ages = userpref.age
                queryset = queryset.filter(map_age_to_q(ages))
        except ObjectDoesNotExist as e:
            pass
        if liked_status is not None:
            queryset = queryset.filter(
                userdog__status=liked_status,
                userdog__user=self.request.user)
        else:
            queryset = queryset.filter().exclude(
                userdog__user=self.request.user)
        return queryset

    def get_object(self):
        pk = self.kwargs.get('pk')
        queryset = self.get_queryset()
        if pk != '-1':
            queryset = queryset.filter(id__gt=pk)
        if len(queryset) == 0:
            raise Http404('No dogs matching query')
        return queryset.first()


class UserDogView(RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.UserDogSerializer

    def put(self, request, *args, **kwargs):
        dog = models.Dog.objects.get(id=self.kwargs['pk'])
        if self.kwargs['liked_status'] == 'undecided':
            try:
                userdog = models.UserDog.objects.filter(dog=dog,
                                                        user=self.request.user
                                                        ).delete()
            except Exception as e:
                raise Http404
        else:
            try:
                userdog, updated = models.UserDog.objects.update_or_create(
                    user=self.request.user,
                    dog=dog,
                    defaults={'status': is_liked(self.kwargs['liked_status'])}
                )
            except Exception:
                raise Http404
        url = reverse('dogview',
                      kwargs={
                          'pk': self.kwargs['pk'],
                          'liked_status': self.kwargs['liked_status']},
                      )
        return Response(data=url, status=status.HTTP_201_CREATED)


class UserPreferenceView(RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    user = get_user_model()
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

    def put(self, request, *args, **kwargs):
        serializer = serializers.UserPrefSerializer(data=self.request.data)
        if serializer.is_valid():
            save_data = serializer.save(user=self.request.user)
        else:
            return Http404('Could not save preferences')
        return HttpResponse('/')
