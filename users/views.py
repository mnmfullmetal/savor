from django.shortcuts import render, redirect
from .forms import UserCreationForm, UserSettingsForm
from datetime import timedelta
from django.contrib.auth import login
from django.core.cache import cache
from pantry.models import Pantry
from .models import UserSettings, Allergen, DietaryRequirement
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from savor.utils import get_cached_json
from django.contrib.auth import get_user_model

User = get_user_model()


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
    user_settings = UserSettings.objects.get(user=user)
    cache_timeout = timedelta(days=7).total_seconds()

    default_allergens = get_cached_json(language='world', data_type='allergens')
    if not default_allergens:
        default_allergens = list(Allergen.objects.values_list('api_tag', 'allergen_name'))
        cache.set('off_allergens_cache_world', default_allergens, timeout=cache_timeout)

    default_requirements = get_cached_json(language='world', data_type='labels')
    if not default_requirements:
        default_requirements =  list(DietaryRequirement.objects.values_list('api_tag', 'requirement_name'))
        cache.set('off_labels_cache_world', default_requirements, timeout=cache_timeout)

    default_languages_data = get_cached_json(language='world', data_type='languages') or {}
    default_languages = [(tag['id'], tag['name']) for tag in default_languages_data.get('tags', [])]

    language_code = user_settings.language_preference
    print(f' language code found! {language_code}')

    localised_allergens_data = None
    localised_requirements_data = None
    localised_languages_data = None
    
    if language_code != 'world':
        print(f'changed language code found! {language_code}')
        localised_allergens_data = get_cached_json(language=language_code, data_type='allergens')
        localised_requirements_data = get_cached_json(language=language_code, data_type='labels')
        localised_languages_data = get_cached_json(language=language_code, data_type="languages")

    localised_allergens = [(tag['id'], tag['name']) for tag in (localised_allergens_data or {}).get('tags', [])]
    allergens = localised_allergens or default_allergens

    localised_requirements = [(tag['id'], tag['name']) for tag in (localised_requirements_data or {}).get('tags', [])]
    requirements = localised_requirements or default_requirements
    
    localised_languages = [(tag['id'], tag['name']) for tag in (localised_languages_data or {}).get('tags', [])]
    languages = localised_languages or default_languages

    form_kwargs = {
        'instance': user_settings,
        'allergens_choices': allergens,
        'requirements_choices': requirements,
        'languages_choices': languages
    }

    if request.method == "POST":
        form = UserSettingsForm(request.POST, **form_kwargs)
        if form.is_valid():
            form.save()
            return redirect('users:account_settings')
        
    else: 
        form = UserSettingsForm(**form_kwargs)

    return render(request, 'users/account_settings.html', {
        'form': form,
        'allergens': allergens ,
        'dietary_requirements': requirements,
        'languages': languages
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
        
     

