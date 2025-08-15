from django.db import models

class SupportGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    members = models.ManyToManyField('authentication.CustomUser', related_name='support_groups')
    moderators = models.ManyToManyField('authentication.CustomUser', related_name='community_moderated_groups')
    is_private = models.BooleanField(default=False)
    max_members = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ForumPost(models.Model):
    author = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE)
    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
