from django.contrib.auth.forms import UserCreationForm
from .models import UserSettings, Allergen, DietaryRequirement
from django.forms import ModelMultipleChoiceField 
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Extends Django's default UserCreationForm to include the 'email' field
    during user registration.
    """
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_(
            "Your password can't be too similar to your other personal information."
            " It must contain at least 8 characters."
            " It can't be a commonly used password."
            " It can't be entirely numeric."
        ),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_("Enter the same password as before, for verification."),
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
        
        labels = {
            'username': _('Username'),
            'email': _('Email'),
        }

        help_texts = {
            'username': _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        }
        

class UserSettingsForm(forms.ModelForm):
    """
    Form for managing user-specific settings.

    This form is designed to have its choice fields (language, country, allergens,
    dietary requirements) dynamically populated in the view with localised data
    fetched from the cache."""
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
        labels = {
            'language_preference': _('Language Preference'),
            'country': _('Country'),
            'allergens': _('Allergens'),
            'dietary_requirements': _('Dietary Requirements'),
            'scan_to_add': _('Enable scan-to-add'),
            'show_nutri_score': _('Display Nutri-Score'),
            'show_eco_score': _('Display Eco-Score'),
            'prioritise_local_results': _('Enable country-localised results'),
        }
        

    def __init__(self, *args, **kwargs):
        # pop custom arguments passed from the view for dynamic choice population
        allergens_choices = kwargs.pop('allergens_choices', Allergen.objects.all())
        requirements_choices = kwargs.pop('requirements_choices', DietaryRequirement.objects.all())
        allergens_labels = kwargs.pop('allergens_labels', None) 
        requirements_labels = kwargs.pop('requirements_labels', None) 
        languages_choices = kwargs.pop('languages_choices', [])
        countries_choices = kwargs.pop('countries_choices', [])
        
        super().__init__(*args, **kwargs)
        
        # set the queryset for many-to-many fields.
        self.fields['allergens'].queryset = allergens_choices
        self.fields['dietary_requirements'].queryset = requirements_choices
        
        # if localised labels are provided, use them for the choices
        # this allows displaying translated names while submitting API tags the backend expects
        if allergens_labels is not None:
             self.fields['allergens'].choices = allergens_labels 

        if requirements_labels is not None:
             self.fields['dietary_requirements'].choices = requirements_labels

        if languages_choices:
             self.fields['language_preference'].choices = languages_choices
        
        if countries_choices:
            self.fields['country'].choices = countries_choices
