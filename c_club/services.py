from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Session, SessionService, Payment, Computer, Service


@transaction.atomic
def start_session(client, computer: Computer, duration_minutes: int, tariff=None):
    if computer.status != Computer.Status.FREE:
        raise ValueError('Компьютер занят')

    hourly_rate = tariff.price_per_hour if tariff else computer.hourly_rate
    total_cost = (Decimal(duration_minutes) / Decimal(60)) * hourly_rate

    session = Session.objects.create(
        client=client, computer=computer, tariff=tariff,
        start_time=timezone.now(),
        duration_minutes=duration_minutes,
        total_cost=total_cost,
        status=Session.Status.ACTIVE,
    )
    computer.status = Computer.Status.BUSY
    computer.save(update_fields=['status'])
    return session


@transaction.atomic
def stop_session(session: Session):
    if session.status != Session.Status.ACTIVE:
        raise ValueError('Сессия уже завершена')

    now = timezone.now()
    session.end_time = now
    session.duration_minutes = int((now - session.start_time).total_seconds() / 60)
    session.status = Session.Status.COMPLETED
    session.save()

    session.computer.status = Computer.Status.FREE
    session.computer.save(update_fields=['status'])

    client = session.client
    if client.balance >= session.total_cost:
        client.balance -= session.total_cost
        client.save(update_fields=['balance'])
        Payment.objects.create(
            client=client, session=session,
            amount=session.total_cost,
            payment_method=Payment.Method.ONLINE,
            payment_type=Payment.Type.SESSION,
        )
    return session


@transaction.atomic
def add_service_to_session(session: Session, service: Service, quantity: int = 1):
    total = service.price * quantity
    SessionService.objects.create(
        session=session, service=service,
        quantity=quantity, total_price=total,
    )
    session.total_cost += total
    session.save(update_fields=['total_cost'])