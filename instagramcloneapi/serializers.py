from rest_framework import serializers

from instagramcloneapi.models import User, Post, Profile

class ProfileDummySerializer(serializers.ModelSerializer):

    '''
    ProfileSerializer
    '''

    class Meta:
        '''
        Meta
        '''
        model = Post
        # depth = 1
        fields = ['image', 'user_id']



class PostSerializer(serializers.ModelSerializer):
    user = ProfileDummySerializer(many=False, read_only=True)

    '''
    PostSerializer
    '''
    class Meta:
        '''
        Meta
        '''
        model = Post
        # depth = 1
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
        # depth = 1
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    '''
    UserSerializer
    '''
    posts = PostSerializer(many=True, read_only=True)
    # profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        '''
        Meta
        '''
        model = User
        fields = '__all__'
