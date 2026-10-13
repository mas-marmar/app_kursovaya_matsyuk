from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser): #пользователи
    class Role(models.TextChoices):
        CLIENT = 'client', 'Клиент'
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        TECHNICIAN = 'technician', 'Техник'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    nickname = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.nickname or self.username


class Tariff(models.Model): #тарифы
    class Type(models.TextChoices):
        HOURLY = 'hourly', 'Почасовой'
        PACKAGE = 'package', 'Пакетный'
        NIGHT = 'night', 'Ночной'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    package_hours = models.PositiveIntegerField(default=0)
    tariff_type = models.CharField(max_length=20, choices=Type.choices, default=Type.HOURLY)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Computer(models.Model): #компы
    class Zone(models.TextChoices):
        STANDARD = 'standard', 'Стандарт'
        VIP = 'vip', 'VIP'
        BOOTCAMP = 'bootcamp', 'Буткемп'

    class Status(models.TextChoices):
        FREE = 'free', 'Свободен'
        BUSY = 'busy', 'Занят'
        MAINTENANCE = 'maintenance', 'Обслуживание'
        BROKEN = 'broken', 'Неисправен'

    name = models.CharField(max_length=50, unique=True)
    zone = models.CharField(max_length=20, choices=Zone.choices, default=Zone.STANDARD)
    cpu = models.CharField(max_length=100, blank=True)
    gpu = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    monitor = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FREE)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Device(models.Model): #уст-ва
    class DeviceType(models.TextChoices):
        MOUSE = 'mouse', 'Мышь'
        KEYBOARD = 'keyboard', 'Клавиатура'
        HEADSET = 'headset', 'Гарнитура'
        MONITOR = 'monitor', 'Монитор'

    class Status(models.TextChoices):
        WORKING = 'working', 'Работает'
        REPAIR = 'repair', 'В ремонте'
        WRITTEN_OFF = 'written_off', 'Списано'

    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name='devices')
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    model = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WORKING)
    purchase_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.get_device_type_display()} — {self.computer.name}'


class Service(models.Model): #услуги
    class Category(models.TextChoices):
        FOOD = 'food', 'Питание'
        DRINK = 'drink', 'Напитки'
        PERIPHERAL = 'peripheral', 'Периферия'
        OTHER = 'other', 'Прочее'

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Session(models.Model): #сессии
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активна'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    computer = models.ForeignKey(Computer, on_delete=models.PROTECT, related_name='sessions')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f'Сессия #{self.pk} ({self.client})'


class SessionService(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Payment(models.Model): #оплата
    class Method(models.TextChoices):
        CASH = 'cash', 'Наличные'
        CARD = 'card', 'Карта'
        ONLINE = 'online', 'Онлайн'

    class Type(models.TextChoices):
        TOPUP = 'topup', 'Пополнение баланса'
        SESSION = 'session', 'Оплата сессии'
        SERVICE = 'service', 'Оплата услуги'

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    payment_type = models.CharField(max_length=20, choices=Type.choices)
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model): #бронь
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        CONFIRMED = 'confirmed', 'Подтверждено'
        CANCELLED = 'cancelled', 'Отменено'
        COMPLETED = 'completed', 'Завершено'

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)