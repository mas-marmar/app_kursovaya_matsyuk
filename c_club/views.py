from django.views import View
from django.http import JsonResponse
from json import loads
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    User, Tariff, Computer, Device, Service,
    Session, Payment, Booking, SessionService
)
from .forms import (
    RegisterForm, TariffForm, ComputerForm, 
    ServiceForm, BookingForm
)

# ==========================================================
#  HTML СТРАНИЦЫ
# ==========================================================
def index_page(request):
    computers = Computer.objects.all().order_by('name')
    return render(request, 'index.html', {'computers': computers})

def services_page(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'services.html', {'services': services})

def clients_page(request):
    clients = User.objects.filter(role='client').order_by('-date_joined')
    return render(request, 'clients.html', {'clients': clients})

# ==========================================================
#  АУТЕНТИФИКАЦИЯ И ПОЛЬЗОВАТЕЛИ
# ==========================================================
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            form = RegisterForm(loads(request.body))
            if form.is_valid():
                user = form.save()
                return JsonResponse({'id': user.id, 'status': 'success'}, status=201)
            return JsonResponse({'status': 'error', 'errors': form.errors, 'code': 400}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    def get(self, request):
        users = User.objects.filter(role='client')
        data = [{'id': u.id, 'username': u.username, 'nickname': u.nickname, 'balance': float(u.balance)} for u in users]
        return JsonResponse({'data': data})

@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    def get(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        return JsonResponse({'id': u.id, 'username': u.username, 'nickname': u.nickname, 'balance': float(u.balance)})

@method_decorator(csrf_exempt, name='dispatch')
class BalanceTopUpView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        try:
            new_data = loads(request.body)
            amount = new_data.get('amount')
            if not amount:
                return JsonResponse({'status': 'error', 'message': 'amount required', 'code': 400}, status=400)

            amount_dec = Decimal(str(amount))
            if amount_dec <= 0:
                return JsonResponse({'status': 'error', 'message': 'amount must be positive', 'code': 400}, status=400)

            with transaction.atomic():
                user.balance += amount_dec
                user.save(update_fields=['balance'])
                Payment.objects.create(
                    client=user, amount=amount_dec,
                    payment_method=new_data.get('payment_method', 'online'),
                    payment_type='topup',
                )
            return JsonResponse({'status': 'success', 'balance': float(user.balance)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

# ==========================================================
#  СПРАВОЧНИКИ
# ==========================================================
@method_decorator(csrf_exempt, name='dispatch')
class TariffListView(View):
    def get(self, request):
        items = Tariff.objects.all()
        data = [{'id': t.id, 'name': t.name, 'price_per_hour': float(t.price_per_hour)} for t in items]
        return JsonResponse({'data': data})

    def post(self, request):
        try:
            form = TariffForm(loads(request.body))
            if form.is_valid():
                obj = form.save()
                return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)
            return JsonResponse({'status': 'error', 'errors': form.errors, 'code': 400}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ComputerListView(View):
    def get(self, request):
        items = Computer.objects.all()
        data = [{'id': c.id, 'name': c.name, 'status': c.status, 'hourly_rate': float(c.hourly_rate)} for c in items]
        return JsonResponse({'data': data})

    def post(self, request):
        try:
            form = ComputerForm(loads(request.body))
            if form.is_valid():
                obj = form.save()
                return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)
            return JsonResponse({'status': 'error', 'errors': form.errors, 'code': 400}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ServiceListView(View):
    def get(self, request):
        items = Service.objects.all()
        data = [{'id': s.id, 'name': s.name, 'price': float(s.price)} for s in items]
        return JsonResponse({'data': data})

    def post(self, request):
        try:
            form = ServiceForm(loads(request.body))
            if form.is_valid():
                obj = form.save()
                return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)
            return JsonResponse({'status': 'error', 'errors': form.errors, 'code': 400}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

# ==========================================================
#  СЕССИИ
# ==========================================================
@method_decorator(csrf_exempt, name='dispatch')
class SessionListView(View):
    def get(self, request):
        items = Session.objects.all()
        data = [{'id': s.id, 'client_id': s.client_id, 'computer_id': s.computer_id, 'status': s.status, 'total_cost': float(s.total_cost)} for s in items]
        return JsonResponse({'data': data})

    def post(self, request):
        try:
            new_data = loads(request.body)
            client_id = new_data.get('client_id')
            computer_id = new_data.get('computer_id')
            duration = int(new_data.get('duration_minutes', 60))
            tariff_id = new_data.get('tariff_id')

            client = User.objects.get(pk=client_id)
            computer = Computer.objects.get(pk=computer_id)

            if computer.status != 'free':
                return JsonResponse({'status': 'error', 'message': 'computer is busy', 'code': 400}, status=400)

            tariff = Tariff.objects.filter(pk=tariff_id).first() if tariff_id else computer.tariff
            hourly_rate = tariff.price_per_hour if tariff else computer.hourly_rate
            total_cost = (Decimal(duration) / Decimal(60)) * hourly_rate

            with transaction.atomic():
                session = Session.objects.create(
                    client=client, computer=computer, tariff=tariff,
                    start_time=timezone.now(), duration_minutes=duration,
                    total_cost=total_cost, status='active',
                )
                computer.status = 'busy'
                computer.save(update_fields=['status'])

            return JsonResponse({'id': session.id, 'status': 'success'}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'client not found', 'code': 404}, status=404)
        except Computer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'computer not found', 'code': 404}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class SessionStopView(View):
    def post(self, request, pk):
        session = get_object_or_404(Session, pk=pk)
        if session.status != 'active':
            return JsonResponse({'status': 'error', 'message': 'session is not active', 'code': 400}, status=400)
        try:
            now = timezone.now()
            session.end_time = now
            session.duration_minutes = int((now - session.start_time).total_seconds() / 60)
            session.status = 'completed'
            
            with transaction.atomic():
                session.save()
                session.computer.status = 'free'
                session.computer.save(update_fields=['status'])
                client = session.client
                if client.balance >= session.total_cost:
                    client.balance -= session.total_cost
                    client.save(update_fields=['balance'])
                    Payment.objects.create(
                        client=client, session=session, amount=session.total_cost,
                        payment_method='online', payment_type='session',
                    )
            return JsonResponse({'status': 'success', 'message': 'session stopped'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class SessionAddServiceView(View):
    def post(self, request, pk):
        session = get_object_or_404(Session, pk=pk)
        try:
            new_data = loads(request.body)
            service_id = new_data.get('service_id')
            quantity = int(new_data.get('quantity', 1))

            service = Service.objects.get(pk=service_id, is_active=True)
            total = service.price * quantity

            with transaction.atomic():
                SessionService.objects.create(session=session, service=service, quantity=quantity, total_price=total)
                session.total_cost += total
                session.save(update_fields=['total_cost'])

            return JsonResponse({'status': 'success', 'total_cost': float(session.total_cost)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

# ==========================================================
#  ПЛАТЕЖИ, БРОНИ, АНАЛИТИКА
# ==========================================================
@method_decorator(csrf_exempt, name='dispatch')
class PaymentListView(View):
    def get(self, request):
        items = Payment.objects.all()
        data = [{'id': p.id, 'client_id': p.client_id, 'amount': float(p.amount), 'type': p.payment_type} for p in items]
        return JsonResponse({'data': data})

@method_decorator(csrf_exempt, name='dispatch')
class BookingListView(View):
    def get(self, request):
        items = Booking.objects.all()
        data = [{'id': b.id, 'client_id': b.client_id, 'computer_id': b.computer_id, 'status': b.status} for b in items]
        return JsonResponse({'data': data})

    def post(self, request):
        try:
            new_data = loads(request.body)
            form = BookingForm(new_data)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.client = User.objects.get(pk=new_data.get('client_id'))
                booking.save()
                return JsonResponse({'id': booking.id, 'status': 'success'}, status=201)
            return JsonResponse({'status': 'error', 'errors': form.errors, 'code': 400}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': 400}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class RevenueReportView(View):
    def get(self, request):
        days = int(request.GET.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        payments = Payment.objects.filter(created_at__gte=since)
        return JsonResponse({
            'period_days': days,
            'total_revenue': float(payments.aggregate(s=Sum('amount'))['s'] or 0),
        })

@method_decorator(csrf_exempt, name='dispatch')
class LoadReportView(View):
    def get(self, request):
        days = int(request.GET.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        sessions = Session.objects.filter(start_time__gte=since)
        return JsonResponse({
            'period_days': days,
            'total_sessions': sessions.count(),
            'busy_computers': Computer.objects.filter(status='busy').count(),
        })