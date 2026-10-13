from django.views import View
from django.http import JsonResponse
from json import loads
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import (
    User, Tariff, Computer, Device, Service,
    Session, Payment, Booking,
)
from .forms import (
    RegisterForm, TariffForm, ComputerForm, DeviceForm,
    ServiceForm, SessionForm, PaymentForm, BookingForm,
)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    # POST /api/register/ - регистрация клиента

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)
        form = RegisterForm(new_data)

        if form.is_valid():
            user = form.save()
            return JsonResponse({'id': user.id, 'status': 'success'}, status=201)

        return JsonResponse(
            {'status': 'error', 'errors': form.errors, 'code': 400},
            status=400
        )

@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    # GET /api/users/ - список клиентов

    def get(self, request):
        users = User.objects.filter(role='client')
        data = []
        for u in users:
            data.append({
                'id': u.id,
                'username': u.username,
                'nickname': u.nickname,
                'email': u.email,
                'phone': u.phone,
                'balance': float(u.balance),
                'is_blocked': u.is_blocked,
            })
        return JsonResponse({'data': data})


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    # GET /api/users/<pk>/ - один пользователь

    def get(self, request, pk):
        u = get_object_or_404(User, pk=pk)
        return JsonResponse({
            'id': u.id,
            'username': u.username,
            'nickname': u.nickname,
            'email': u.email,
            'phone': u.phone,
            'balance': float(u.balance),
            'is_blocked': u.is_blocked,
        })


@method_decorator(csrf_exempt, name='dispatch')
class BalanceTopUpView(View):
    # POST /api/users/<pk>/topup/ - пополнить баланс

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        raw_json = request.body
        new_data = loads(raw_json)

        amount = new_data.get('amount')
        if not amount or float(amount) <= 0:
            return JsonResponse(
                {'status': 'error', 'message': 'amount required', 'code': 400},
                status=400
            )

        user.balance += float(amount)
        user.save(update_fields=['balance'])

        Payment.objects.create(
            client=user,
            amount=amount,
            payment_method=new_data.get('payment_method', 'online'),
            payment_type='topup',
        )

        return JsonResponse({'status': 'success', 'balance': float(user.balance)})



@method_decorator(csrf_exempt, name='dispatch')
class TariffListView(View): # тарифы
    # GET /api/tariffs/ - список
    # POST /api/tariffs/ - создать

    def get(self, request):
        items = Tariff.objects.all()
        data = []
        for t in items:
            data.append({
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'price_per_hour': float(t.price_per_hour),
                'package_hours': t.package_hours,
                'tariff_type': t.tariff_type,
                'is_active': t.is_active,
            })
        return JsonResponse({'data': data})

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)
        form = TariffForm(new_data)

        if form.is_valid():
            obj = form.save()
            return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)

        return JsonResponse(
            {'status': 'error', 'errors': form.errors, 'code': 400},
            status=400
        )

@method_decorator(csrf_exempt, name='dispatch')
class TariffDetailView(View):
    # GET /api/tariffs/<pk>/

    def get(self, request, pk):
        t = get_object_or_404(Tariff, pk=pk)
        return JsonResponse({
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'price_per_hour': float(t.price_per_hour),
            'package_hours': t.package_hours,
            'tariff_type': t.tariff_type,
            'is_active': t.is_active,
        })



@method_decorator(csrf_exempt, name='dispatch')
class ComputerListView(View): # компы
    # GET /api/computers/ - список
    # POST /api/computers/ - создать

    def get(self, request):
        items = Computer.objects.all()
        data = []
        for c in items:
            data.append({
                'id': c.id,
                'name': c.name,
                'zone': c.zone,
                'cpu': c.cpu,
                'gpu': c.gpu,
                'ram': c.ram,
                'status': c.status,
                'hourly_rate': float(c.hourly_rate),
                'tariff_id': c.tariff_id,
            })
        return JsonResponse({'data': data})

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)
        form = ComputerForm(new_data)

        if form.is_valid():
            obj = form.save()
            return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)

        return JsonResponse(
            {'status': 'error', 'errors': form.errors, 'code': 400},
            status=400
        )

@method_decorator(csrf_exempt, name='dispatch')
class ComputerDetailView(View):
    # GET /api/computers/<pk>/

    def get(self, request, pk):
        c = get_object_or_404(Computer, pk=pk)
        devices = [{'id': d.id, 'type': d.device_type, 'model': d.model, 'status': d.status}
                   for d in c.devices.all()]
        return JsonResponse({
            'id': c.id,
            'name': c.name,
            'zone': c.zone,
            'cpu': c.cpu,
            'gpu': c.gpu,
            'ram': c.ram,
            'monitor': c.monitor,
            'status': c.status,
            'hourly_rate': float(c.hourly_rate),
            'tariff_id': c.tariff_id,
            'devices': devices,
        })



@method_decorator(csrf_exempt, name='dispatch')
class DeviceListView(View): # устройства
    # GET /api/devices/ - список
    # POST /api/devices/ - создать

    def get(self, request):
        items = Device.objects.all()
        data = []
        for d in items:
            data.append({
                'id': d.id,
                'computer_id': d.computer_id,
                'device_type': d.device_type,
                'model': d.model,
                'status': d.status,
                'purchase_date': d.purchase_date,
            })
        return JsonResponse({'data': data})

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)
        form = DeviceForm(new_data)

        if form.is_valid():
            obj = form.save()
            return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)

        return JsonResponse(
            {'status': 'error', 'errors': form.errors, 'code': 400},
            status=400
        )

@method_decorator(csrf_exempt, name='dispatch')
class DeviceDetailView(View):
    # GET /api/devices/<pk>/

    def get(self, request, pk):
        d = get_object_or_404(Device, pk=pk)
        return JsonResponse({
            'id': d.id,
            'computer_id': d.computer_id,
            'device_type': d.device_type,
            'model': d.model,
            'status': d.status,
            'purchase_date': d.purchase_date,
        })



@method_decorator(csrf_exempt, name='dispatch')
class ServiceListView(View): #услуги
    # GET /api/services/ - список
    # POST /api/services/ - создать

    def get(self, request):
        items = Service.objects.all()
        data = []
        for s in items:
            data.append({
                'id': s.id,
                'name': s.name,
                'category': s.category,
                'price': float(s.price),
                'is_active': s.is_active,
            })
        return JsonResponse({'data': data})

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)
        form = ServiceForm(new_data)

        if form.is_valid():
            obj = form.save()
            return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)

        return JsonResponse(
            {'status': 'error', 'errors': form.errors, 'code': 400},
            status=400
        )

@method_decorator(csrf_exempt, name='dispatch')
class ServiceDetailView(View):
    # GET /api/services/<pk>/

    def get(self, request, pk):
        s = get_object_or_404(Service, pk=pk)
        return JsonResponse({
            'id': s.id,
            'name': s.name,
            'category': s.category,
            'price': float(s.price),
            'is_active': s.is_active,
        })



@method_decorator(csrf_exempt, name='dispatch')
class SessionListView(View): # сессии
    # GET /api/sessions/ - список
    # POST /api/sessions/start/ - открыть

    def get(self, request):
        items = Session.objects.all()
        data = []
        for s in items:
            data.append({
                'id': s.id,
                'client_id': s.client_id,
                'client_name': s.client.nickname or s.client.username,
                'computer_id': s.computer_id,
                'computer_name': s.computer.name,
                'tariff_id': s.tariff_id,
                'start_time': s.start_time,
                'end_time': s.end_time,
                'duration_minutes': s.duration_minutes,
                'total_cost': float(s.total_cost),
                'status': s.status,
            })
        return JsonResponse({'data': data})

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)

        client_id = new_data.get('client_id')
        computer_id = new_data.get('computer_id')
        duration = new_data.get('duration_minutes', 60)
        tariff_id = new_data.get('tariff_id')

        if not client_id or not computer_id:
            return JsonResponse(
                {'status': 'error', 'message': 'client_id and computer_id required', 'code': 400},
                status=400
            )

        try:
            client = User.objects.get(pk=client_id)
            computer = Computer.objects.get(pk=computer_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'client not found', 'code': 404}, status=404)
        except Computer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'computer not found', 'code': 404}, status=404)

        if computer.status != 'free':
            return JsonResponse(
                {'status': 'error', 'message': 'computer is busy', 'code': 400},
                status=400
            )

        from decimal import Decimal
        from django.utils import timezone

        tariff = Tariff.objects.filter(pk=tariff_id).first() if tariff_id else None
        hourly_rate = tariff.price_per_hour if tariff else computer.hourly_rate
        total_cost = (Decimal(duration) / Decimal(60)) * hourly_rate

        session = Session.objects.create(
            client=client,
            computer=computer,
            tariff=tariff,
            start_time=timezone.now(),
            duration_minutes=duration,
            total_cost=total_cost,
            status='active',
        )
        computer.status = 'busy'
        computer.save(update_fields=['status'])

        return JsonResponse({'id': session.id, 'status': 'success'}, status=201)



@method_decorator(csrf_exempt, name='dispatch')
class SessionDetailView(View):
    # GET /api/sessions/<pk>/

    def get(self, request, pk):
        s = get_object_or_404(Session, pk=pk)
        return JsonResponse({
            'id': s.id,
            'client_id': s.client_id,
            'computer_id': s.computer_id,
            'tariff_id': s.tariff_id,
            'start_time': s.start_time,
            'end_time': s.end_time,
            'duration_minutes': s.duration_minutes,
            'total_cost': float(s.total_cost),
            'status': s.status,
        })

@method_decorator(csrf_exempt, name='dispatch')
class SessionStopView(View):
    # POST /api/sessions/<pk>/stop/ - завершить сессию

    def post(self, request, pk):
        session = get_object_or_404(Session, pk=pk)

        if session.status != 'active':
            return JsonResponse(
                {'status': 'error', 'message': 'session is not active', 'code': 400},
                status=400
            )

        from django.utils import timezone
        now = timezone.now()
        session.end_time = now
        session.duration_minutes = int((now - session.start_time).total_seconds() / 60)
        session.status = 'completed'
        session.save()

        session.computer.status = 'free'
        session.computer.save(update_fields=['status'])

        client = session.client
        if client.balance >= session.total_cost:
            client.balance -= session.total_cost
            client.save(update_fields=['balance'])
            Payment.objects.create(
                client=client,
                session=session,
                amount=session.total_cost,
                payment_method='online',
                payment_type='session',
            )

        return JsonResponse({'status': 'success', 'message': 'session stopped'})

@method_decorator(csrf_exempt, name='dispatch')
class SessionAddServiceView(View):
    # POST /api/sessions/<pk>/add-service/ - добавить услугу в сессию

    def post(self, request, pk):
        session = get_object_or_404(Session, pk=pk)
        raw_json = request.body
        new_data = loads(raw_json)

        service_id = new_data.get('service_id')
        quantity = int(new_data.get('quantity', 1))

        if not service_id:
            return JsonResponse(
                {'status': 'error', 'message': 'service_id required', 'code': 400},
                status=400
            )

        service = Service.objects.filter(pk=service_id, is_active=True).first()
        if not service:
            return JsonResponse(
                {'status': 'error', 'message': 'service not found', 'code': 404},
                status=404
            )

        total = service.price * quantity

        from .models import SessionService
        SessionService.objects.create(
            session=session,
            service=service,
            quantity=quantity,
            total_price=total,
        )
        session.total_cost += total
        session.save(update_fields=['total_cost'])

        return JsonResponse({'status': 'success', 'total_cost': float(session.total_cost)})

@method_decorator(csrf_exempt, name='dispatch')
class PaymentListView(View): # платежи
    # GET /api/payments/ - список
    # POST /api/payments/ - создать

    def get(self, request):
        items = Payment.objects.all()
        data = []
        for p in items:
            data.append({
                'id': p.id,
                'client_id': p.client_id,
                'session_id': p.session_id,
                'amount': float(p.amount),
                'payment_method': p.payment_method,
                'payment_type': p.payment_type,
                'created_at': p.created_at,
            })
        return JsonResponse({'data': data})

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)
        form = PaymentForm(new_data)

        if form.is_valid():
            obj = form.save()
            return JsonResponse({'id': obj.id, 'status': 'success'}, status=201)

        return JsonResponse(
            {'status': 'error', 'errors': form.errors, 'code': 400},
            status=400
        )

@method_decorator(csrf_exempt, name='dispatch')
class PaymentDetailView(View):
    # GET /api/payments/<pk>/

    def get(self, request, pk):
        p = get_object_or_404(Payment, pk=pk)
        return JsonResponse({
            'id': p.id,
            'client_id': p.client_id,
            'session_id': p.session_id,
            'amount': float(p.amount),
            'payment_method': p.payment_method,
            'payment_type': p.payment_type,
            'created_at': p.created_at,
        })




@method_decorator(csrf_exempt, name='dispatch')
class BookingListView(View): # брони
    # GET /api/bookings/ - список
    # POST /api/bookings/ - создать

    def get(self, request):
        items = Booking.objects.all()
        data = []
        for b in items:
            data.append({
                'id': b.id,
                'client_id': b.client_id,
                'computer_id': b.computer_id,
                'start_time': b.start_time,
                'end_time': b.end_time,
                'status': b.status,
                'created_at': b.created_at,
            })
        return JsonResponse({'data': data})

    def post(self, request):
        raw_json = request.body
        new_data = loads(raw_json)
        form = BookingForm(new_data)

        if form.is_valid():
            booking = form.save(commit=False)

            client_id = new_data.get('client_id')
            if client_id:
                client = User.objects.filter(pk=client_id).first()
                if not client:
                    return JsonResponse(
                        {'status': 'error', 'message': 'client not found', 'code': 404},
                        status=404
                    )
                booking.client = client
            else:
                return JsonResponse(
                    {'status': 'error', 'message': 'client_id required', 'code': 400},
                    status=400
                )

            booking.save()
            return JsonResponse({'id': booking.id, 'status': 'success'}, status=201)

        return JsonResponse(
            {'status': 'error', 'errors': form.errors, 'code': 400},
            status=400
        )


@method_decorator(csrf_exempt, name='dispatch')
class BookingDetailView(View):
    # GET /api/bookings/<pk>/

    def get(self, request, pk):
        b = get_object_or_404(Booking, pk=pk)
        return JsonResponse({
            'id': b.id,
            'client_id': b.client_id,
            'computer_id': b.computer_id,
            'start_time': b.start_time,
            'end_time': b.end_time,
            'status': b.status,
            'created_at': b.created_at,
        })


@method_decorator(csrf_exempt, name='dispatch')
class RevenueReportView(View):
    # GET /api/analytics/revenue/?days=30

    def get(self, request):
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta

        try:
            days = int(request.GET.get('days', 30))
        except (TypeError, ValueError):
            days = 30

        since = timezone.now() - timedelta(days=days)
        payments = Payment.objects.filter(created_at__gte=since)

        total = payments.aggregate(s=Sum('amount'))['s'] or 0
        count = payments.count()

        return JsonResponse({
            'period_days': days,
            'total_revenue': float(total),
            'payments_count': count,
        })


@method_decorator(csrf_exempt, name='dispatch')
class LoadReportView(View):
    # GET /api/analytics/load/?days=7

    def get(self, request):
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta

        try:
            days = int(request.GET.get('days', 7))
        except (TypeError, ValueError):
            days = 7

        since = timezone.now() - timedelta(days=days)
        sessions = Session.objects.filter(start_time__gte=since)

        total_sessions = sessions.count()
        total_minutes = sessions.aggregate(m=Sum('duration_minutes'))['m'] or 0

        return JsonResponse({
            'period_days': days,
            'total_sessions': total_sessions,
            'total_minutes': total_minutes,
            'busy_computers': Computer.objects.filter(status='busy').count(),
            'total_computers': Computer.objects.count(),
        })