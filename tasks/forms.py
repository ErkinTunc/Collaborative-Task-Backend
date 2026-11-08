from django import forms 
from .models import UserProfile,Team,Task
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.widgets import DateTimeInput

from django.db.models import Q

# For creating users (it is not login)
class CustomUserForm(UserCreationForm): # this will ask user 2 times its password and hash it
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
 
# for Updates       
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

# extra updates for users
class UserProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = UserProfile
        fields = ['description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'image': forms.ImageField(label="Profile picture", widget=forms.ClearableFileInput(attrs={'class':'form-control'}))
        }

class TeamForm(forms.ModelForm):
        users = forms.ModelMultipleChoiceField(queryset=User.objects.all(),widget=forms.CheckboxSelectMultiple,required=False)
        # NOTE: Always use "ModelMultipleChoiceField" instead od "ModelMultipleChoiceField" because it causes problems in chousing(or do extra work) or face the consequences
    
        class Meta: # a meta class which will hold the data
            model = Team
            fields = ['name',"users"]
            widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control','placeholder':"Team Name"}),
                
            }


class TaskForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)

        if user.is_superuser:
            allowed_teams = Team.objects.all()
        elif self.instance.pk:
            allowed_teams = Team.objects.filter(
                Q(users=user) | Q(tasks=self.instance)
            ).distinct()
        else:
            allowed_teams = Team.objects.filter(users=user)

        self.fields["teams"].queryset = allowed_teams

    class Meta:
        model = Task

        fields = [
            "title","private","status","deadline",
            "description","users","teams",
        ]

        widgets = {
            "deadline": DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            )
        }
