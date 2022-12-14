from django.db import models


def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class User(models.Model):
    phoneNumber = models.CharField(max_length=14, blank=True, null=True, unique=True)
    email = models.CharField(max_length=100, blank=True, null=True, default='', unique=True)
    password = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "User Model"


class Profile(models.Model):
    username = models.CharField(max_length=100, blank=False, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True, default='')
    image = models.URLField(max_length=512, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE, unique=True)

class Post(models.Model):
    title = models.CharField(max_length=200, blank=True)
    description = models.CharField(
        max_length=400, blank=True, null=True, default='')
    image = models.URLField(max_length=512, blank=True, null=True)
    user = models.ForeignKey(Profile, related_name='posts',
                             on_delete=models.CASCADE, db_column='user_id')
    created = models.DateTimeField(auto_now_add=True)
