from rest_framework import serializers

from instagramcloneapi.models import User, Post, Profile


class PostSerializer(serializers.ModelSerializer):
    '''
    PostSerializer
    '''
    class Meta:
        '''
        Meta
        '''
        model = Post
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    '''
    ProfileSerializer
    '''

    class Meta:
        '''
        Meta
        '''
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    '''
    UserSerializer
    '''
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        '''
        Meta
        '''
        model = User
        fields = '__all__'
