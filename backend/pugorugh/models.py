from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

dog_genders = ['m', 'f', 'u']
dog_sizes = ['s', 'm', 'l', 'xl', 'u']
userdog_statuses = ['l', 'd']
userpref_genders = ['m', 'f']
userpref_sizes = ['s', 'm', 'l', 'xl']
userpref_ages = ['b', 'y', 'a', 's']


def validate_dog_gender(value):
    """ Validator for dog gender:
        "m" for male, "f" for female, "u" for unknown
    :param value: string, one character
    :return: raise validation error if not in m,f,u
    """
    if value not in dog_genders:
        raise ValidationError('Dog gender must be in {}'.format(dog_genders))


def validate_dog_size(value):
    """ Validator for dog size:
        "s" for small, "m" for medium, "l" for large,
        "xl" for extra large, "u" for unknown
    :param value: string, one character
    :return: raise validation error if not in s,m,l,xl,u
    """
    if value not in dog_sizes:
        raise ValidationError('Dog size must be in {}'.format(dog_sizes))


def validate_userdog_status(value):
    """ Validator for userdog status:
        "l" for liked, "d" for disliked
    :param value: string, one character
    :return: raise validation error if not in l,d
    """
    if value not in userdog_statuses:
        raise ValidationError(
            'Dog size must be in {}'.format(userdog_statuses))


def validate_userpref_gender(value):
    """ Validator for userpref gender:
        "m" for male, "f" for female
    :param value: string, comma-separated values
    :return: raise validation error if not in m,f
    """
    values = value.split(',')
    for value in values:
        if len(value) > 1 or value not in userpref_genders:
            raise ValidationError(
                'Must be in {}, comma separated'.format(userpref_genders))


def validate_userpref_size(value):
    """ Validator for userpref size:
        "s" for small, "m" for medium, "l" for large, "xl" for extra large
    :param value: string, comma-separated values
    :return: raise validation error if not in s,m,l,xl
    """
    values = value.split(',')
    for value in values:
        if value not in userpref_sizes:
            raise ValidationError(
                'Must be in {}, comma separated'.format(userpref_sizes))


def validate_userpref_age(value):
    """ Validator for userpref size:
        "b" for baby, "y" for young, "a" for adult, "s" for senior
    :param value: string, comma-separated values
    :return: raise validation error if not in b,y,a,s
    """
    values = value.split(',')
    for value in values:
        if len(value) > 1 or value not in userpref_ages:
            raise ValidationError(
                'Must be {}, comma separated'.format(userpref_ages))


class Dog(models.Model):
    name = models.CharField(max_length=100)
    image_filename = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(blank=True,
                              null=True)  # for months
    gender = models.CharField(max_length=5,
                              blank=True,
                              validators=[validate_dog_gender])
    size = models.CharField(max_length=5,
                            blank=True,
                            validators=[validate_dog_size])

    def __str__(self):
        return '{} {} {}'.format(self.name, self.breed, self.id)


class UserDog(models.Model):
    user = models.ForeignKey(User)
    dog = models.ForeignKey(Dog,
                            related_name='userdog',
                            on_delete=models.CASCADE)
    status = models.CharField(max_length=1,
                              validators=[validate_userdog_status])
    unique_together = (user, dog)


class UserPref(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    age = models.CharField(max_length=10,
                           validators=[validate_userpref_age],
                           blank=True)
    gender = models.CharField(max_length=10,
                              validators=[validate_userpref_gender],
                              blank=True)
    size = models.CharField(max_length=10,
                            validators=[validate_userpref_size],
                            blank=True)
