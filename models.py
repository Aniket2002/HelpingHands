from django.db import models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, date


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField()
    role = models.TextField()

    def __str__(self):
        return str(self.user)


class Blog(models.Model):
    title = models.CharField(max_length=255)
    blog_summary = models.CharField(max_length=1000, default='Random Title Summary')
    blog_category = models.CharField(max_length=255, default='Random Title Category')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    Date = models.DateField(auto_now_add=True)
    body = models.TextField()

    def __str__(self):
        return self.title + ' | ' + str(self.author)

    def get_absolute_url(self):
        return reverse('Home Page')
