from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import PatientSignUpForm


def register(request):
    if request.user.is_authenticated:
        return redirect('appointments:dashboard')

    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('appointments:dashboard')
    else:
        form = PatientSignUpForm()

    return render(request, 'accounts/register.html', {'form': form})


class HospitalLoginView(LoginView):
    template_name = 'accounts/login.html'


class HospitalLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
