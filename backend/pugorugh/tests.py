from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from .models import Dog, UserDog, UserPref
from .views import DogView, UserPreferenceView, UserDogView
import random
import string
from rest_framework.test import APIRequestFactory, force_authenticate, \
    APITestCase
from rest_framework.authtoken.models import Token

# Create your tests here.


dog_genders = ['m', 'f', 'u']
dog_sizes = ['s', 'm', 'l', 'xl']
userdog_statuses = ['l', 'd']
user_preference_dict = {'gender': ['m', 'f'],
                        'size': ['s', 'm', 'l', 'xl'],
                        'age': ['b', 'y', 'a', 's']}


def make_random_name(name_length):
    return ''.join(
        random.choice(string.ascii_lowercase) for x in range(name_length)
    )


class PugOrTestCase(APITestCase):

    def setUp(self):
        # create test user
        self.user = User.objects.create_superuser(
            username='wanchan',
            email='wanchan@doggo.cat',
            password='wanchan')
        self.token = Token.objects.create(user=self.user)
        self.token.save()

        # create three dogs with random attributes
        num_dogs = 3
        test_dogs = []
        for i in range(0, num_dogs):
            name = make_random_name(5)
            new_test_dog = Dog(
                name=name,
                image_filename='.'.join([name, 'img']),
                breed='whuffie',
                age=random.randrange(100),
                gender=random.choice(dog_genders),
                size=random.choice(dog_sizes))
            test_dogs.append(new_test_dog)
        Dog.objects.bulk_create(test_dogs)

        # assign liked status
        userdogs = []
        all_dogs = Dog.objects.all()
        for i, is_liked in enumerate(['l', 'd']):
            new_userdog = UserDog(user=self.user,
                                  dog=all_dogs[i],
                                  status=is_liked)
            userdogs.append(new_userdog)
        UserDog.objects.bulk_create(userdogs)

        # Set up request factory
        self.factory = APIRequestFactory()

    def get_dogs(self, liked_status=None, user=None):
        if user is None:
            return Dog.objects.all().filter(userdog__status=liked_status)
        else:
            return Dog.objects.all().exclude(userdog__user=self.user)

    def get_dog_dict(self):
        dog_dict = {'liked': self.get_dogs(liked_status='l'),
                    'disliked': self.get_dogs(liked_status='d'),
                    'undecided': self.get_dogs(user=self.user)}
        return dog_dict

    def testDbContents(self):
        self.assertEqual(Dog.objects.count(), 3)
        self.assertEqual(User.objects.count(), 1)

    def testUserPrefView(self):

        userpref = {'user': self.user,
                    'gender': 'm,f,u',
                    'size': 's,m,l,xl',
                    'age': 'b,y,a,s'}
        new_userpref = UserPref.objects.create(**userpref)

        request = self.factory.get(
            reverse('userpref'),
            HTTP_AUTHORIZATION='Token {}'.format(self.token))
        force_authenticate(request, user=self.user)
        view = UserPreferenceView.as_view()

        resp = view(request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['gender'], 'm,f,u')
        self.assertEqual(resp.data['size'], 's,m,l,xl')
        self.assertEqual(resp.data['age'], 'b,y,a,s')

    def testDogViewAndUserPref(self):

        request_kwargs = {'pk': -1,
                          'liked_status': 'liked'}
        request = self.factory.get(
            reverse('dogview_minus', kwargs=request_kwargs),
            HTTP_AUTHORIZATION='Token {}'.format(self.token))
        force_authenticate(request, user=self.user)
        view = DogView.as_view()

        # Get a dog and find attribute
        liked_status = 'liked'
        dog = self.get_dog_dict()[liked_status].first()

        # Set userpref to like everyone and check results - one dog
        userpref = {'user': self.user,
                    'gender': 'm,f,u',
                    'size': 's,m,l,xl',
                    'age': 'b,y,a,s'}
        new_userpref = UserPref.objects.create(**userpref)

        userprefs = UserPref.objects.all()[0]

        resp = view(request, pk=-1, liked_status=liked_status)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], dog.name)

        # Update userpref to exclude dog and check results - no dogs
        testing_gender = dog.gender
        genders = ['m', 'f', 'u']
        genders.pop(genders.index(testing_gender))
        genders = ','.join(genders)

        userpref['gender'] = genders
        new_userpref = UserPref.objects.update(**userpref)

        resp = view(request, pk=-1, liked_status=liked_status)
        self.assertEqual(resp.status_code, 404)

    def testDogViewMinus(self):

        dog_dict = self.get_dog_dict()

        request_kwargs = {'pk': -1,
                          'liked_status': 'liked'}
        request = self.factory.get(
            reverse('dogview_minus', kwargs=request_kwargs),
            HTTP_AUTHORIZATION='Token {}'.format(self.token))
        force_authenticate(request, user=self.user)
        view = DogView.as_view()

        for liked_status in dog_dict.keys():
            resp = view(request, pk=-1, liked_status=liked_status)
            if len(dog_dict[liked_status]) > 0:
                first_dog = dog_dict[liked_status].first()
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.data['name'], first_dog.name)
            else:
                # handle where dogs returned is zero
                self.assertEqual(resp.status_code, 404)

    def testUserDogView(self):
        # 1. Find liked dog
        # Note: liked is always pk=1 based on setUp

        old_liked_status = 'liked'
        new_liked_status = 'disliked'
        dog_dict = self.get_dog_dict()
        test_dog = dog_dict[old_liked_status].values()[0]

        pk = test_dog['id']

        # 2. Change status to disliked
        put_request_kwargs = {'pk': pk, 'liked_status': old_liked_status}
        get_request_kwargs = {'pk': -1, 'liked_status': new_liked_status}

        put_request = self.factory.put(
            reverse('userdogview', kwargs=put_request_kwargs),
            HTTP_AUTHORIZATION='Token {}'.format(self.token))
        get_request = self.factory.get(
            reverse('dogview_minus', kwargs=get_request_kwargs),
            HTTP_AUTHORIZATION='Token {}'.format(self.token))

        force_authenticate(put_request, user=self.user)
        force_authenticate(get_request, user=self.user)

        put_view = UserDogView.as_view()
        get_view = DogView.as_view()

        # Update and check results from DogView
        put_resp = put_view(put_request, pk=pk, liked_status=new_liked_status)
        self.assertEqual(put_resp.status_code, 201)

        get_resp = get_view(get_request, pk=-1, liked_status=new_liked_status)
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.data['name'], test_dog['name'])

        # Revert and check
        put_resp = put_view(put_request, pk=pk, liked_status=old_liked_status)
        self.assertEqual(put_resp.status_code, 201)

        get_resp = get_view(get_request, pk=-1, liked_status=old_liked_status)
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.data['name'], test_dog['name'])
