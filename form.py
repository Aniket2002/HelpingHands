from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms


class RegForm(UserCreationForm):
        first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        bio = forms.CharField(max_length=300, widget=forms.Textarea(attrs={'class': 'form-control'}))
        email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
        Phone_Number = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
        role = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

        class Meta:
            model = User
            fields = ('username', 'first_name', 'last_name', 'email', 'Phone_Number', 'bio', 'role', 'password1',
                      'password2')


        def __init__(self, *args, **kwargs):
            super(RegForm, self).__init__(*args, **kwargs)

            self.fields['username'].widget.attrs['class'] = 'form-control'
            self.fields['password1'].widget.attrs['class'] = 'form-control'
            self.fields['password2'].widget.attrs['class'] = 'form-control'


class EditForm(UserChangeForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    Phone_Number = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    date_joined = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'Phone_Number', 'date_joined')
