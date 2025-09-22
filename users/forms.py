from django.contrib.auth.forms import UserCreationForm
from .models import User, UserSettings, Allergen, DietaryRequirement
from django import forms

class UserCreationForm(UserCreationForm):
     class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class UserSettingsForm(forms.ModelForm):
    
    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    dietary_requirements = forms.ModelMultipleChoiceField(
        queryset=DietaryRequirement.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserSettings
        fields = ['allergens', 'dietary_requirements', 'show_nutri_score', 'show_eco_score', 'country', 'get_only_localized_results']
    