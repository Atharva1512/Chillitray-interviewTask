from rest_framework import serializers
from django.contrib.auth.models import User
from .models import login_history
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password']


class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = login_history
        fields = "__all__"

    # def validate(self,attrs):
    #     if User.objects.filter(email=attrs['email']).exists():
    #         raise serializers.ValidationError({'email',('Email already taken')})
    #         return super().validate(attrs)

    # def create(self,validated_data):
    #     user = User.objects.create_user(
    #         username=validate_data["username"],
    #         first_name=validate_data["first_name"],
    #         last_name=validate_data["last_name"],
    #         email=validate_data["email"],
    #         password=validate_data["password"],

    #     )
    #     return user
