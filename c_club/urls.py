from django.urls import path
from . import views

urlpatterns = [
    # --- HTML Страницы ---
    path('', views.index_page, name='index'),
    path('services-page/', views.services_page, name='services-page'),
    path('clients-page/', views.clients_page, name='clients-page'),

    # --- API Маршруты ---
    path('api/register/', views.RegisterView.as_view()),
    
    # Пользователи
    path('api/users/', views.UserListView.as_view()),
    path('api/users/<int:pk>/', views.UserDetailView.as_view()),
    path('api/users/<int:pk>/topup/', views.BalanceTopUpView.as_view()),

    # Тарифы
    path('api/tariffs/', views.TariffListView.as_view()),

    # Компьютеры
    path('api/computers/', views.ComputerListView.as_view()),

    # Услуги
    path('api/services/', views.ServiceListView.as_view()),

    # Сессии
    path('api/sessions/', views.SessionListView.as_view()),
    path('api/sessions/<int:pk>/stop/', views.SessionStopView.as_view()),
    path('api/sessions/<int:pk>/add-service/', views.SessionAddServiceView.as_view()),

    # Платежи
    path('api/payments/', views.PaymentListView.as_view()),

    # Брони
    path('api/bookings/', views.BookingListView.as_view()),

    # Аналитика
    path('api/analytics/revenue/', views.RevenueReportView.as_view()),
    path('api/analytics/load/', views.LoadReportView.as_view()),
]