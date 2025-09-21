from django.shortcuts import render, redirect
from .forms import UserCreationForm, PasswordResetForm
from django.contrib.auth import login
from pantry.models import Pantry

# Create your views here.

def register(request):
    if request.method =="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Pantry.objects.create(user = user )
            login(request, user)
            return redirect('pantry:index')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
    

def profile_view(request):
    return render(request, 'users/profile.html')

