from django import forms
from .models import (
    User, Tariff, Computer, Device, Service,
    Session, Payment, Booking,
)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'phone']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'description', 'price_per_hour', 'package_hours', 'tariff_type', 'is_active']


class ComputerForm(forms.ModelForm):
    class Meta:
        model = Computer
        fields = ['name', 'zone', 'cpu', 'gpu', 'ram', 'monitor', 'status', 'hourly_rate', 'tariff']


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['computer', 'device_type', 'model', 'status', 'purchase_date']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'category', 'price', 'is_active']


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['computer', 'tariff', 'duration_minutes']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['session', 'amount', 'payment_method', 'payment_type']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['computer', 'start_time', 'end_time']