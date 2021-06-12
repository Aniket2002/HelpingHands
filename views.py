from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .form import RegForm, EditForm

class PasswordChange(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('login')

class DoctorRegister(generic.CreateView):
    form_class = RegForm
    template_name = 'registration/user.html'
    success_url = reverse_lazy('login')

class Page(generic.View):
    template_name = 'registration/dpage.html'
    success_url = reverse_lazy('dpage.html')

class UserEdit(generic.UpdateView):
    form_class = EditForm
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('homepage:Home Page')

    def get_object(self, queryset=None):
        return self.request.user
