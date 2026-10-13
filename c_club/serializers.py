from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (User, Computer, Device, Tariff, Service,
                     Session, SessionService, Payment, Booking)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'email', 'phone',
                  'balance', 'role', 'date_joined')
        read_only_fields = ('id', 'balance', 'role', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'nickname', 'email', 'phone', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class ComputerSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True)
    zone_display = serializers.CharField(source='get_zone_display', read_only=True)

    class Meta:
        model = Computer
        fields = ('id', 'name', 'zone', 'zone_display', 'cpu', 'gpu', 'ram',
                  'monitor', 'status', 'hourly_rate', 'tariff', 'devices')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class SessionServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = SessionService
        fields = ('id', 'service', 'service_name', 'quantity', 'total_price')


class SessionSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    computer_name = serializers.CharField(source='computer.name', read_only=True)
    services = SessionServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ('id', 'client', 'computer', 'computer_name', 'tariff',
                  'start_time', 'end_time', 'duration_minutes',
                  'total_cost', 'status', 'services', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at',)


class BookingSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    computer_name = serializers.CharField(source='computer.name', read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'client', 'computer', 'computer_name',
                  'start_time', 'end_time', 'status', 'created_at')
        read_only_fields = ('created_at',)