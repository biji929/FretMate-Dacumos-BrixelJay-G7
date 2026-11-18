from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="First Name")
    last_name = forms.CharField(max_length=50, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial=UserProfile.ROLE_GUITARIST,
        label="Account Role",
        help_text="Choose 'Guitarist' to practice & log sessions, or 'Instructor' to curate songs & oversee students."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.help_text = None
            field.widget.attrs.update({
                'class': 'w-full bg-gray-50 dark:bg-gray-700/60 border border-gray-300 dark:border-gray-600 rounded-lg p-2.5 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email address is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '').strip()
        user.last_name = self.cleaned_data.get('last_name', '').strip()
        user.email = self.cleaned_data.get('email', '').strip().lower()
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data.get('role', UserProfile.ROLE_GUITARIST)
            profile.save()
        return user


class UserProfileUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True, label="First Name")
    last_name = forms.CharField(max_length=50, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    contact_number = forms.CharField(max_length=25, required=False, label="Contact Number")
    bio = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'rows': 3}), label="Bio")
    skill_level = forms.ChoiceField(choices=UserProfile.SKILL_LEVELS, required=False, label="Guitar Skill Level")
    weekly_goal_minutes = forms.IntegerField(min_value=10, max_value=3000, required=False, label="Weekly Goal (minutes)")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        initial = kwargs.get('initial', {})
        if user:
            initial.update({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            })
            profile = getattr(user, 'profile', None)
            if profile:
                initial.update({
                    'contact_number': profile.contact_number,
                    'bio': profile.bio,
                    'skill_level': profile.skill_level,
                    'weekly_goal_minutes': profile.weekly_goal_minutes,
                })
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg p-2.5 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        # Check if email is already used by another user
        existing = User.objects.filter(email__iexact=email)
        if self.user:
            existing = existing.exclude(pk=self.user.pk)
        if existing.exists():
            raise forms.ValidationError("This email address is already in use by another account.")
        return email

    def save(self):
        if not self.user:
            return None
        self.user.first_name = self.cleaned_data['first_name'].strip()
        self.user.last_name = self.cleaned_data['last_name'].strip()
        self.user.email = self.cleaned_data['email'].strip().lower()
        self.user.save()

        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.contact_number = self.cleaned_data.get('contact_number', '').strip()
        profile.bio = self.cleaned_data.get('bio', '').strip()
        if 'skill_level' in self.cleaned_data and self.cleaned_data['skill_level']:
            profile.skill_level = self.cleaned_data['skill_level']
        if 'weekly_goal_minutes' in self.cleaned_data and self.cleaned_data['weekly_goal_minutes']:
            profile.weekly_goal_minutes = self.cleaned_data['weekly_goal_minutes']
        profile.save()
        return self.user


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg p-2 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
