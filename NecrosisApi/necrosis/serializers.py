# Serializer for user registration and validation
from rest_framework import serializers
from .models import User, AnalysisSession
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

class UserSerializer(serializers.ModelSerializer):
    # Password field is write-only and validated
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'user_type', 'contact', 'organisation')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'user_type': {'default': 'regular'},
            'contact': {'required': False, 'allow_blank': True, 'allow_null': True},
            'organisation': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    # Username must be letters only (no numbers)
    username_validator = RegexValidator(r'^[A-Za-z]+$', 'Username must contain only letters.')

    def validate_username(self, value):
        self.username_validator(value)
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    def validate(self, data):
        # Only validate passwords if both are present (i.e., registration or password change)
        if 'password' in data or 'confirm_password' in data:
            if data.get('password') != data.get('confirm_password'):
                raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            user_type=validated_data.get('user_type', 'regular'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AnalysisSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisSession
        fields = ['session_id', 'created_at', 'num_images', 'notes', 'session_name']
        read_only_fields = ['session_id', 'created_at', 'num_images', 'notes']
