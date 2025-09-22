from django.shortcuts import render, redirect
from .forms import UserCreationForm, UserSettingsForm
from django.contrib.auth import login
from pantry.models import Pantry
from .models import User, UserSettings, Allergen, DietaryRequirement
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .utils import get_localised_allergens_and_requirements


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
    user = request.user
    user_settings, created = UserSettings.objects.get_or_create(user=user)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            return redirect('users:account_settings')
        
    else: 
        form = UserSettingsForm(instance=user_settings)

    country_code = user_settings.country
    
    db_allergens = dict(Allergen.objects.values_list('api_tag', 'allergen_name'))
    db_dietary_reqs = dict(DietaryRequirement.objects.values_list('api_tag', 'requirement_name'))
    
    localised_api_allergens, localised_api_dietary_reqs = get_localised_allergens_and_requirements(country_code)

    combined_allergens = []
    for tag in localised_api_allergens:
        api_tag = tag.get('id')
        name = tag.get('name')
        if name and name.lower() == api_tag.lower():
            name = db_allergens.get(api_tag, name)
        combined_allergens.append({'id': api_tag, 'name': name})

    combined_dietary_reqs = []
    relevant_tags = ['en:halal', 'en:kosher', 'en:no-lactose', 'en:vegan', 'en:vegetarian', 'en:no-gluten']
    for tag in localised_api_dietary_reqs:
        api_tag = tag.get('id')
        name = tag.get('name')
        if api_tag in relevant_tags:
            if name and name.lower() == api_tag.lower():
                name = db_dietary_reqs.get(api_tag, name)
            combined_dietary_reqs.append({'id': api_tag, 'name': name})
            
 
    return render(request, 'users/account_settings.html', {
        'form': form,
        'allergens': combined_allergens,
        'dietary_reqs': combined_dietary_reqs,
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
        
     

