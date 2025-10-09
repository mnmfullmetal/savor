from django.contrib.auth.forms import UserCreationForm
from .models import UserSettings, Allergen, DietaryRequirement
from django.forms import ModelMultipleChoiceField 
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationForm(UserCreationForm):
     class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
        

class UserSettingsForm(forms.ModelForm):
    language_preference = forms.ChoiceField(required=False)
    country = forms.ChoiceField(required=False)

    allergens = ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        to_field_name='api_tag' 
    )

    dietary_requirements = ModelMultipleChoiceField(
        queryset=DietaryRequirement.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        to_field_name='api_tag' 
    )

    class Meta:
        model = UserSettings
        fields = ['allergens', 'dietary_requirements', 'language_preference', 'country', 'scan_to_add', 'show_nutri_score', 'show_eco_score', 'prioritise_local_results']
        

    def __init__(self, *args, **kwargs):
        allergens_choices = kwargs.pop('allergens_choices', Allergen.objects.all())
        requirements_choices = kwargs.pop('requirements_choices', DietaryRequirement.objects.all())
        allergens_labels = kwargs.pop('allergens_labels', None) 
        requirements_labels = kwargs.pop('requirements_labels', None) 
        languages_choices = kwargs.pop('languages_choices', [])
        countries_choices = kwargs.pop('countries_choices', [])
        
        super().__init__(*args, **kwargs)
        
        self.fields['allergens'].queryset = allergens_choices
        self.fields['dietary_requirements'].queryset = requirements_choices
        
        if allergens_labels is not None:
             self.fields['allergens'].choices = allergens_labels 

        if requirements_labels is not None:
             self.fields['dietary_requirements'].choices = requirements_labels

        if languages_choices:
             self.fields['language_preference'].choices = languages_choices
        
        if countries_choices:
            self.fields['country'].choices = countries_choices
