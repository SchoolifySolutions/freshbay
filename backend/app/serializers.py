from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FoodBank, FoodSource
User = get_user_model()

class GeoapifyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodSource
        fields = ['id', 'name', 'category', 'address', 'latitude', 'longitude', 'api_response']

class FoodSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodSource
        fields = ['id', 'name', 'contact_email', 'contact_phone', 'owner', 'latitude', 'longitude', 'source_type']



class FoodBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodBank
        fields = ['name', 'latitude', 'longitude', 'street_address', 'city', 'zip_code', 'phone', 'web_link']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'date_of_birth', 'username', 'gender', 'phone_number', 'location', 'medication', 'guardian')


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)