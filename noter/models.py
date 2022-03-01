from django.db import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Note(models.Model):
    def create_now():
        now = datetime.now().date()
        return now

    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    content = models.CharField(max_length=120)
    deadline = models.DateField(editable=True, default=create_now)
    is_done = models.BooleanField(default=False)
    created = models.DateField(editable=False, default=create_now)
    modified = models.DateField(default=create_now)

    def __str__(self):
        return print(f'note {self.content}, created at: {self.created} by: {self.user}')