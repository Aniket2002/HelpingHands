from django import forms
from django.forms import ModelForm
from .models import Appointment, TherapyGoal, TherapistReview, Therapist

class TherapistSearchForm(forms.Form):
    specialty = forms.ChoiceField(
        choices=[('', 'Any Specialty')] + Therapist.SPECIALIZATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    therapy_type = forms.ChoiceField(
        choices=[('', 'Any Type')] + Therapist.THERAPY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    max_rate = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max hourly rate'})
    )
    
    insurance = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insurance provider'})
    )
    
    language = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Language spoken'})
    )

class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        fields = ['session_type', 'notes_before']
        widgets = {
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'notes_before': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What would you like to discuss in this session?'
            }),
        }

class TherapyGoalForm(ModelForm):
    class Meta:
        model = TherapyGoal
        fields = ['category', 'title', 'description', 'target_date']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Goal title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your goal in detail'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class ReviewForm(ModelForm):
    class Meta:
        model = TherapistReview
        fields = ['rating', 'communication_rating', 'effectiveness_rating', 'review_text', 'would_recommend']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'communication_rating': forms.Select(choices=[(i, f'{i} stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'effectiveness_rating': forms.Select(choices=[(i, f'{i} stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this therapist...'
            }),
            'would_recommend': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        }
