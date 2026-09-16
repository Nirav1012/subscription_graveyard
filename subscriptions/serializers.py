from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    monthly_cost = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'name', 'cost', 'billing_cycle', 'category',
            'next_renewal_date', 'status', 'created_at', 'monthly_cost',
        ]
        read_only_fields = ['id', 'created_at']


from .models import CheckIn


class CheckInSerializer(serializers.ModelSerializer):
    subscription_name = serializers.ReadOnlyField(source='subscription.name')

    class Meta:
        model = CheckIn
        fields = ['id', 'subscription', 'subscription_name', 'asked_at', 'response', 'responded_at']
        read_only_fields = ['id', 'subscription', 'asked_at', 'responded_at']