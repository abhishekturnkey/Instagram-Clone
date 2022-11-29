from instagramcloneapi.models import User, Post, Profile
from instagramcloneapi.serializers import UserSerializer, PostSerializer, ProfileSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.views import APIView

import jwt
from datetime import datetime
from boto3.session import Session

import os

import random

BUCKET_NAME = 'BUCKET_NAME'
ACCESS_KEY_ID = "ACCESS_KEY_ID"
SECRET_ACCESS_KEY = "SECRET_ACCESS_KEY"


class CreateResponse:
    '''
    Creates custom response
    '''

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": True,
        "Access-Control-Allow-Headers":
        "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE",
        "Access-Control-Max-Age": "86400",
        "Access-Control-Expose-Headers":
        "Access-Control-Allow-Origin, Access-Control-Allow-Credentials, Access-Control-Allow-Headers, Access-Control-Allow-Methods, Access-Control-Max-Age"
    }

    @staticmethod
    def success(data=None, status_code=status.HTTP_200_OK, message="Request processed successfully"):
        '''success response'''

        response_data = {}

        if data is None:
            response_data = {
                "status": True,
                "message": message,
                "code": status_code
            }
        else:
            response_data = {
                "status": True,
                "message": message,
                "code": status_code,
                "data": data
            }

        return Response(response_data, status=status_code, headers=CreateResponse.headers)

    @staticmethod
    def failed(data=None, status_code=status.HTTP_400_BAD_REQUEST, message="Failed to process request"):
        '''error response'''
        response_data = {}

        if data is None:
            response_data = {
                "status": False,
                "message": message,
                "code": status_code
            }
        else:
            response_data = {
                "status": False,
                "message": message,
                "code": status_code,
                "data": data
            }

        return Response(response_data, status=status_code, headers=CreateResponse.headers)


class JwtToken:
    '''
    JWT_TOKEN
    '''
    @staticmethod
    def encode(payload):
        '''
        returns jwt token
        '''
        return jwt.encode(payload, 'secretKey', algorithm='HS256')

    @staticmethod
    def decode(token):
        '''
        returns payload
        '''
        return jwt.decode(token, 'secretKey', algorithms=['HS256'])


class RegisterView(APIView):
    '''
    RegisterView
    '''

    def post(self, request):
        '''
        create user
        '''
        try:
            data = JSONParser().parse(request)

            email = None
            phone_number = None
            if "phoneNumber" in data.keys():
                phone_number = data["phoneNumber"]

            if "email" in data.keys():
                email = data["email"]

            password = data['password']

            data_obj = {"phoneNumber": phone_number,
                        "email": email,
                        "password": password}

            user = UserSerializer(data=data_obj)

            if user.is_valid():
                user.save()
                return CreateResponse.success(user.data, status_code=status.HTTP_201_CREATED, message='USER CREATED')

            return CreateResponse.failed("Invalid data", status_code=status.HTTP_400_BAD_REQUEST, message='BAD REQUEST')

        except Exception as exception:
            print(exception)
            return CreateResponse.failed("Failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message='INTERNAL SERVER ERROR')


class LoginView(APIView):
    '''
    Login View
    '''

    def post(self, request):
        '''
        login method
        '''

        try:
            data = JSONParser().parse(request)

            if "phoneNumber" in data.keys():
                phone = data["phoneNumber"]
                password = data['password']

                try:
                    item = User.objects.get(phoneNumber=phone)
                    user = UserSerializer(item, many=False).data

                    if (not user['password'] == password):
                        return CreateResponse.failed(data, status_code=status.HTTP_400_BAD_REQUEST, message='PASSWORD MISMATCH')

                    token = JwtToken.encode(
                        {"email": user['email'], "user_id": user["id"]})

                    return CreateResponse.success(data={"token": token})

                except Exception as exception:
                    print(exception)
                    return CreateResponse.failed(
                        "USER NOT FOUND",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message='INVALID PHONE NUMBER')

            elif "email" in data.keys():
                email = data["email"]
                password = data['password']
                try:
                    item = User.objects.get(email=email)

                    user = UserSerializer(item, many=False).data

                    if (not user['password'] == password):
                        return CreateResponse.failed(data, status_code=status.HTTP_400_BAD_REQUEST, message='PASSWORD MISMATCH')

                    token = JwtToken.encode(
                        {"email": user["email"], "user_id": user["id"]})
                    return CreateResponse.success(data={"token": token})

                except Exception as exception:
                    print(exception)
                    return CreateResponse.failed(
                        "USER NOT FOUND",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message='INVALID EMAIL ID')

            else:
                return CreateResponse.failed(data, status_code=status.HTTP_400_BAD_REQUEST, message='INVALID REQUEST BODY')

        except Exception as exception:
            print(exception)
            return CreateResponse.failed(exception, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message='INTERNAL SERVER ERROR')


class UserFeeds(APIView):
    """
    UserFeeds
    """

    def get(self, request):
        """
        Get all posts
        """
        try:
            token = request.META.get("HTTP_AUTHORIZATION", "")

            if not token:
                return CreateResponse.failed("TOKEN NOT FOUND", status_code=status.HTTP_401_UNAUTHORIZED, message='JWT TOKEN REQUIRED')

            token = token.split(" ")[1]
            try:
                JwtToken.decode(token)
            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "INVALID TOKEN",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='TOKEN VALIDATION FAILED')

            posts = Post.objects.all()
            serializer = PostSerializer(posts, many=True)
            return CreateResponse.success(serializer.data)

        except Exception as exception:
            print(exception)
            return CreateResponse.failed(exception, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message='INTERNAL SERVER ERROR')


class PostView(APIView):
    """
    ProfileView
    """

    def get(self, request):
        """
        get user details
        """
        try:
            token = request.META.get("HTTP_AUTHORIZATION", "")

            if not token:
                return CreateResponse.failed("TOKEN NOT FOUND", status_code=status.HTTP_401_UNAUTHORIZED, message='JWT TOKEN REQUIRED')

            token = token.split(" ")[1]
            try:
                payload = JwtToken.decode(token)
                user_id = payload["user_id"]
            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "INVALID TOKEN",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='TOKEN VALIDATION FAILED')

            try:
                item = Post.objects.filter(user=user_id)
                profile = PostSerializer(item, many=True).data

                return CreateResponse.success(data=profile)

            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "POSTS NOT FOUND",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message='POSTS NOT FOUND')

        except Exception as exception:
            print(exception)
            return CreateResponse.failed("FAILED", status_code=status.HTTP_400_BAD_REQUEST, message='INTERNAL SERVER ERROR')

    def post(self, request):
        """
        update user details
        """

        parser_classes = (MultiPartParser, )
        try:
            token = request.META.get("HTTP_AUTHORIZATION", "")

            if not token:
                return CreateResponse.failed("TOKEN NOT FOUND", status_code=status.HTTP_401_UNAUTHORIZED, message='JWT TOKEN REQUIRED')

            token = token.split(" ")[1]
            try:
                payload = JwtToken.decode(token)
                user_id = payload["user_id"]
            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "INVALID TOKEN",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='TOKEN VALIDATION FAILED')

            try:
                file_extension = os.path.splitext(
                    str(request.FILES['image']))[1]

                filename = f"posts/{user_id}/" + datetime.now().strftime("%d-%m-%YT") + \
                    str(random.randint(10 ** 10, (10 ** 10) * 9)) + file_extension

                session = Session(
                    aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY
                )

                s3 = session.resource('s3')
                s3.Bucket(BUCKET_NAME).put_object(
                    Key=filename, Body=request.FILES['image']
                )

                file_url = f"https://{BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{filename}"

                required_data = {
                    "user": user_id,
                    "image": file_url,
                    "title": request.data["title"],
                    "description": request.data["description"]
                }

                post = PostSerializer(data=required_data)

                if post.is_valid():
                    post.save()
                    return CreateResponse.success(data=post.data)
                else:
                    return CreateResponse.failed(data=required_data, status_code=status.HTTP_400_BAD_REQUEST, message="PROFILE ALREADY CREATED")

            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "ERROR",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message='Failed to create profile')

        except Exception as exception:
            print(exception)
            return CreateResponse.failed("FAILED", status_code=status.HTTP_400_BAD_REQUEST, message='INTERNAL SERVER ERROR')


class ProfileView(APIView):
    """
    ProfileView
    """

    def get(self, request):
        """
        get user details
        """
        try:
            token = request.META.get("HTTP_AUTHORIZATION", "")

            if not token:
                return CreateResponse.failed("TOKEN NOT FOUND", status_code=status.HTTP_401_UNAUTHORIZED, message='JWT TOKEN REQUIRED')

            token = token.split(" ")[1]
            try:
                payload = JwtToken.decode(token)
                user_id = payload["user_id"]
            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "INVALID TOKEN",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='TOKEN VALIDATION FAILED')

            try:
                item = Profile.objects.get(user=user_id)
                profile = ProfileSerializer(item, many=False).data

                return CreateResponse.success(data=profile)

            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "NOT FOUND",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message='PROFILE NOT FOUND')

        except Exception as exception:
            print(exception)
            return CreateResponse.failed("FAILED", status_code=status.HTTP_400_BAD_REQUEST, message='INTERNAL SERVER ERROR')

    def post(self, request):
        """
        update user details
        """

        parser_classes = (MultiPartParser, )
        try:
            token = request.META.get("HTTP_AUTHORIZATION", "")

            if not token:
                return CreateResponse.failed("TOKEN NOT FOUND", status_code=status.HTTP_401_UNAUTHORIZED, message='JWT TOKEN REQUIRED')

            token = token.split(" ")[1]
            try:
                payload = JwtToken.decode(token)
                user_id = payload["user_id"]
            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "INVALID TOKEN",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='TOKEN VALIDATION FAILED')

            try:
                file_extension = os.path.splitext(
                    str(request.FILES['image']))[1]

                filename = f"profile/{str(user_id)}/" + datetime.now().strftime("%d-%m-%YT") + \
                    str(random.randint(10 ** 10, (10 ** 10) * 9)) + file_extension

                session = Session(
                    aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY
                )

                s3 = session.resource('s3')
                s3.Bucket('sample-bucket-hic').put_object(
                    Key=filename, Body=request.FILES['image'])

                file_url = f"https://{BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{filename}"

                required_data = {
                    "user": user_id,
                    "image": file_url,
                    "username": request.data["username"],
                    "name": request.data["name"]
                }

                profile = ProfileSerializer(data=required_data)

                if profile.is_valid():
                    profile.save()
                    return CreateResponse.success(data=profile.data)
                else:
                    return CreateResponse.failed(data=required_data, status_code=status.HTTP_400_BAD_REQUEST, message="PROFILE ALREADY CREATED")

            except Exception as exception:
                print(exception)
                return CreateResponse.failed(
                    "ERROR",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message='Failed to create profile')

        except Exception as exception:
            print(exception)
            return CreateResponse.failed("FAILED", status_code=status.HTTP_400_BAD_REQUEST, message='INTERNAL SERVER ERROR')
