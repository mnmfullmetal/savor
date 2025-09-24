from django.contrib.auth.forms import UserCreationForm
from .models import UserSettings
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationForm(UserCreationForm):
     class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = UserSettings
        fields = ['allergens', 'dietary_requirements', 'language_preference', 'show_nutri_score', 'show_eco_score', 'get_only_localized_results']
    
    def __init__(self, *args, **kwargs):
        allergens_choices = kwargs.pop('allergens_choices', [])
        requirements_choices = kwargs.pop('requirements_choices', [])
        languages_choices = kwargs.pop('languages_choices', [])

        super().__init__(*args, **kwargs)
        if allergens_choices:
            self.fields['allergens'].choices = allergens_choices
        
        if requirements_choices:
            self.fields['dietary_requirements'].choices = requirements_choices

        if languages_choices:
            self.fields['language_preference'].choices = languages_choices