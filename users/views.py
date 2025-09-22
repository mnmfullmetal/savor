from django.shortcuts import render, redirect
from .forms import UserCreationForm
from django.contrib.auth import login
from pantry.models import Pantry
from .models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required


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
    
@login_required
def account_settings(request):

    return render(request, 'users/account_settings.html', {
         'user': request.user,
    })

@login_required
def delete_user(request):
        try: 
            user_to_delete = User.objects.get(id=request.user.id)
            user_to_delete.delete()
            return HttpResponseRedirect(reverse('login'))

        except Exception as e:
            print('error deleteing user: {e}')
            return JsonResponse({'error: could not delete user account'}, status=500)
            

