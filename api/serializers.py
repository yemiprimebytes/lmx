from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User
import random
from django.core.cache import cache


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_student', 'is_lecturer', 'gender', 'phone')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'gender', 'is_student', 'is_lecturer')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender'),
            is_student=validated_data.get('is_student', False),
            is_lecturer=validated_data.get('is_lecturer', False),
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        
        # Retrieve OTP from Redis
        cached_otp = cache.get(f"otp_{email}")
        
        if cached_otp is None:
            raise serializers.ValidationError("OTP expired or not found.")
        if cached_otp != otp:
            raise serializers.ValidationError("Invalid OTP.")
            
        return data