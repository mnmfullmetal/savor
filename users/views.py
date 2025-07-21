from django.shortcuts import render, redirect
from .forms import UserCreationForm
from django.contrib.auth import login

# Create your views here.

def register(request):
    if request.method =="POST":
        form = UserCreationForm(request.post)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('pantry:index')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
        
    

def toggle_login():
    pass 

