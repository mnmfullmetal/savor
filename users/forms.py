from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models import User

class UserCreationForm(UserCreationForm):
     class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

