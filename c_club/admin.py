from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, Tariff, Computer, Device, Service,
                     Session, SessionService, Payment, Booking)

admin.site.register(User, UserAdmin)

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'status', 'hourly_rate')
    list_filter = ('zone', 'status')
    search_fields = ('name',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'computer', 'status', 'total_cost', 'start_time')
    list_filter = ('status',)
    date_hierarchy = 'start_time'

admin.site.register([Tariff, Device, Service, SessionService, Payment, Booking])