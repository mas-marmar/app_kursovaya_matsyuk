from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Tariff, Computer, Device, Service,
    Session, SessionService, Payment, Booking
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'nickname', 'role', 'balance', 'is_blocked')
    list_filter = ('role', 'is_blocked', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'nickname', 'phone', 'balance', 'is_blocked')}),
    )

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'tariff_type', 'price_per_hour', 'is_active')
    list_filter = ('tariff_type', 'is_active')

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    # Добавили monitor в отображение
    list_display = ('name', 'zone', 'monitor', 'status', 'hourly_rate', 'tariff')
    list_filter = ('zone', 'status')
    search_fields = ('name', 'cpu', 'gpu')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_type', 'model', 'computer', 'status')
    list_filter = ('device_type', 'status')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'computer', 'start_time', 'status', 'total_cost')
    list_filter = ('status', 'start_time')
    readonly_fields = ('start_time',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'amount', 'payment_method', 'payment_type', 'created_at')
    list_filter = ('payment_method', 'payment_type', 'created_at')

admin.site.register(SessionService)
admin.site.register(Booking)