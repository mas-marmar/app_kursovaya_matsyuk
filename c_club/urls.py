from django.urls import path
from .views import (
    RegisterView,
    UserListView, UserDetailView, BalanceTopUpView,
    TariffListView, TariffDetailView,
    ComputerListView, ComputerDetailView,
    DeviceListView, DeviceDetailView,
    ServiceListView, ServiceDetailView,
    SessionListView, SessionDetailView, SessionStopView, SessionAddServiceView,
    PaymentListView, PaymentDetailView,
    BookingListView, BookingDetailView,
    RevenueReportView, LoadReportView,
)

urlpatterns = [
    # Аутентификация / пользователи
    path('register/', RegisterView.as_view()),
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserDetailView.as_view()),
    path('users/<int:pk>/topup/', BalanceTopUpView.as_view()),

    # Тарифы
    path('tariffs/', TariffListView.as_view()),
    path('tariffs/<int:pk>/', TariffDetailView.as_view()),

    # Компьютеры
    path('computers/', ComputerListView.as_view()),
    path('computers/<int:pk>/', ComputerDetailView.as_view()),

    # Устройства
    path('devices/', DeviceListView.as_view()),
    path('devices/<int:pk>/', DeviceDetailView.as_view()),

    # Услуги
    path('services/', ServiceListView.as_view()),
    path('services/<int:pk>/', ServiceDetailView.as_view()),

    # Сессии
    path('sessions/', SessionListView.as_view()),
    path('sessions/<int:pk>/', SessionDetailView.as_view()),
    path('sessions/<int:pk>/stop/', SessionStopView.as_view()),
    path('sessions/<int:pk>/add-service/', SessionAddServiceView.as_view()),

    # Платежи
    path('payments/', PaymentListView.as_view()),
    path('payments/<int:pk>/', PaymentDetailView.as_view()),

    # Бронирования
    path('bookings/', BookingListView.as_view()),
    path('bookings/<int:pk>/', BookingDetailView.as_view()),

    # Аналитика
    path('analytics/revenue/', RevenueReportView.as_view()),
    path('analytics/load/', LoadReportView.as_view()),
]