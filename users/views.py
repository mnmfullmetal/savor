from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, UserSettingsForm
from django.contrib.auth import login
from pantry.models import Pantry
from .models import UserSettings, Allergen, DietaryRequirement
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from savor.utils import get_cached_json, LANGUAGE_CODE_MAP
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.

def register(request):
    """
    Handles user registration.

    On successful form submission, it creates a new user, an associated pantry,
    logs the user in, and redirects to the homepage.
    """
    if request.method =="POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Pantry.objects.create(user = user )
            login(request, user)
            return redirect('pantry:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

    
@login_required
def account_settings(request):
    """
    Manages the user settings form, handling both display and updates.

    This view dynamically populates form choices (allergens, languages, etc.)
    with localized names based on the user's language preference. It fetches
    this data from a Redis cache, which is populated by background Celery tasks,
    to ensure a fast and internationalized user experience.
    """
    user = request.user
    user_settings = UserSettings.objects.get(user=user)
    
    # fetch allergens and requirements from the db to serve as a base
    default_allergens = Allergen.objects.all()
    default_requirements = DietaryRequirement.objects.all() 
    
    db_allergen_tags = set(default_allergens.values_list('api_tag', flat=True))
    db_requirement_tags = set(default_requirements.values_list('api_tag', flat=True))

    # fetch default english data from cache for form choices as a fallback
    default_languages_data = get_cached_json(language_code='en', data_type='languages') or {}
    default_languages_choices = sorted(
        [(tag['id'], tag['name']) for tag in default_languages_data.get('tags', []) if tag['id'] in LANGUAGE_CODE_MAP.keys()] , 
        key=lambda x: x[1]
    )
    # ensure english can always be navigated back to via a "deafult" option
    default_languages_choices.insert(0, ('en', 'Default (English)'))

    default_countries_data = get_cached_json(language_code='en', data_type='countries') or {}
    countries_choices = sorted(
        [(tag['id'], tag['name']) for tag in default_countries_data.get('tags', []) if tag.get('name')] ,
            key=lambda x: x[1] 
    )

    user_language = user_settings.language_preference
    language_code = LANGUAGE_CODE_MAP.get(user_language, 'en')

    # initialise choices with english names that will be overridden with localised names if a preference is set
    allergens_queryset = default_allergens
    requirements_queryset = default_requirements
    allergens_labels = list(default_allergens.values_list('api_tag', 'allergen_name')) 
    requirements_labels = list(default_requirements.values_list('api_tag', 'requirement_name'))
    languages_choices = default_languages_choices
    
    # if user has a language preference other than english, fetch localised data from the cache to build the form
    if language_code and language_code != 'en':
        
        localised_allergens_data = get_cached_json(language_code=language_code, data_type='allergens')
        if localised_allergens_data and localised_allergens_data.get('tags'):
             allergens_labels = sorted(
                 [(tag['id'], tag['name']) 
                  for tag in localised_allergens_data.get('tags') 
                  if tag['id'] in db_allergen_tags],
                 key=lambda x: x[1]
             )
             
        localised_requirements_data = get_cached_json(language_code=language_code, data_type='labels') 
        if localised_requirements_data and localised_requirements_data.get('tags'):
             requirements_labels = sorted(
                 [(tag['id'], tag['name']) 
                  for tag in localised_requirements_data.get('tags') 
                  if tag['id'] in db_requirement_tags],
                 key=lambda x: x[1] 
             )
             
        localised_languages_data = get_cached_json(language_code=language_code, data_type='languages')
        if localised_languages_data and localised_languages_data.get('tags'):
             languages_choices = sorted(
                 [(tag['id'], tag['name']) 
                  for tag in localised_languages_data['tags'] 
                  if tag.get('name') and tag['id'] in LANGUAGE_CODE_MAP.keys()],
                 key=lambda x: x[1] 
             )
             languages_choices.insert(0, ('en', 'Default (English)'))

        localised_countries_data = get_cached_json(language_code=language_code, data_type='countries')
        if localised_countries_data and localised_countries_data.get('tags'):
            countries_choices = sorted(
                 [(tag['id'], tag['name']) 
                  for tag in localised_countries_data.get('tags') 
                  if tag.get('name')],
                 key=lambda x: x[1] 
            )
        
    # kwargs to dynamically initialise the UserSettingsForm with correct and possibly localied choices.
    form_kwargs = {
        'instance': user_settings,
        'allergens_choices': allergens_queryset,        
        'requirements_choices': requirements_queryset,  
        'allergens_labels': allergens_labels,            
        'requirements_labels': requirements_labels,      
        'languages_choices': languages_choices,
        'countries_choices': countries_choices
    }

    if request.method == "POST":
        form = UserSettingsForm(request.POST, **form_kwargs)
        if form.is_valid():
            settings_instance = form.save(commit=False)
            settings_instance.save()
            form.save_m2m()
            return redirect('users:account_settings')
        
    else: 
        form = UserSettingsForm(**form_kwargs)

    return render(request, 'users/account_settings.html', {
        'form': form,
        'allergens': allergens_queryset ,
        'dietary_requirements': requirements_queryset,
        'languages': languages_choices,
        'countries_choices': countries_choices
    })


@login_required
def delete_user(request):
        """
        Handles the permanent deletion of the currently logged-in user's account.
        """
        try: 
            user_to_delete = User.objects.get(id=request.user.id)
            user_to_delete.delete()
            return HttpResponseRedirect(reverse('login'))

        except Exception as e:
            print('error deleteing user: {e}')
            return JsonResponse({'error: could not delete user account'}, status=500)
        
     
