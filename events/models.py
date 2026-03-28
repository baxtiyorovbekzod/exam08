from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    pass

class Event(models.Model):
    EVENT_TYPES = (
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    location = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='events')

    def clean(self):
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValidationError("Tugash vaqti boshlanish vaqtidan oldin bo'lishi mumkin emas!")
        
        
        if self.event_type == 'OFFLINE' and not self.location:
            raise ValidationError("Offline eventlar uchun joylashuv (location) kiritilishi shart!")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Registration(models.Model):
    STATUS_CHOICES = (
        ('REGISTERED', 'Registered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='REGISTERED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"