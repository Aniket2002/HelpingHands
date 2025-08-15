from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile, TherapistCredentials

class BaseRegistrationForm(forms.ModelForm):
    """Base form for common user registration fields"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a secure password (8+ characters)',
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        }),
        help_text='Your password must contain at least 8 characters.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        }),
        help_text='Enter the same password as before, for verification.'
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username', 'phone_number', 'date_of_birth')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter your first name',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter your last name',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a unique username',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
            }),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ClientRegistrationForm(BaseRegistrationForm):
    """Registration form for clients seeking therapy"""
    emergency_contact_name = forms.CharField(
        label='Emergency Contact Name',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter emergency contact name',
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    emergency_contact_phone = forms.CharField(
        label='Emergency Contact Phone',
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter emergency contact phone',
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    # Mental health related fields
    therapy_goals = forms.CharField(
        label='What are your therapy goals?',
        widget=forms.Textarea(attrs={
            'placeholder': 'Briefly describe what you hope to achieve through therapy...',
            'rows': 3,
            'class': 'w-full pl-3 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        }),
        required=False
    )
    
    preferred_therapist_gender = forms.ChoiceField(
        label='Preferred Therapist Gender',
        choices=[
            ('', 'No preference'),
            ('male', 'Male'),
            ('female', 'Female'),
            ('non_binary', 'Non-binary'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full pl-3 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    therapy_experience = forms.ChoiceField(
        label='Previous Therapy Experience',
        choices=[
            ('none', 'No previous therapy experience'),
            ('some', 'Some previous therapy experience'),
            ('extensive', 'Extensive therapy experience'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full pl-3 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )

    class Meta(BaseRegistrationForm.Meta):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'client'
        user.emergency_contact_name = self.cleaned_data.get('emergency_contact_name')
        user.emergency_contact_phone = self.cleaned_data.get('emergency_contact_phone')
        if commit:
            user.save()
            # Create user profile with additional client information
            profile, created = UserProfile.objects.get_or_create(user=user)
            # You can store therapy_goals, preferred_therapist_gender, etc. in the profile
        return user


class TherapistRegistrationForm(BaseRegistrationForm):
    """Registration form for therapists"""
    license_number = forms.CharField(
        label='Professional License Number',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your license number',
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    specialization = forms.CharField(
        label='Primary Specialization',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Anxiety, Depression, PTSD, Family Therapy',
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    experience_years = forms.IntegerField(
        label='Years of Experience',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter years of professional experience',
            'min': 0,
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    education = forms.CharField(
        label='Education & Degrees',
        widget=forms.Textarea(attrs={
            'placeholder': 'List your degrees, universities, and graduation years...',
            'rows': 3,
            'class': 'w-full pl-3 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    bio = forms.CharField(
        label='Professional Bio',
        widget=forms.Textarea(attrs={
            'placeholder': 'Tell potential clients about your approach, experience, and what makes you unique...',
            'rows': 4,
            'class': 'w-full pl-3 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    hourly_rate = forms.DecimalField(
        label='Hourly Rate ($)',
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter your hourly rate',
            'min': 0,
            'step': '0.01',
            'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200'
        })
    )
    
    accepts_insurance = forms.BooleanField(
        label='I accept insurance payments',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
        })
    )

    class Meta(BaseRegistrationForm.Meta):
        pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'therapist'
        if commit:
            user.save()
            
            # Create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.specialization = self.cleaned_data.get('specialization', '')
            profile.experience_years = self.cleaned_data.get('experience_years', 0)
            profile.bio = self.cleaned_data.get('bio', '')
            profile.hourly_rate = self.cleaned_data.get('hourly_rate', 0)
            profile.is_accepting_clients = True
            profile.save()
            
            # Create therapist credentials (pending verification)
            credentials, created = TherapistCredentials.objects.get_or_create(user=user)
            credentials.education = self.cleaned_data.get('education', '')
            credentials.verification_status = 'pending'
            credentials.save()
            
        return user


# Keep the old form for backward compatibility
class CustomUserCreationForm(ClientRegistrationForm):
    """Legacy form - redirects to ClientRegistrationForm"""
    pass
