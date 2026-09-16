from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('flagged', 'Flagged'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES)
    category = models.CharField(max_length=50, blank=True)
    next_renewal_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def monthly_cost(self):
        return self.cost if self.billing_cycle == 'monthly' else self.cost / 12

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class CheckIn(models.Model):
    RESPONSE_CHOICES = [
        ('still_use', 'Still Use'),
        ('not_sure', 'Not Sure'),
        ('dont_use', "Don't Use"),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='checkins')
    asked_at = models.DateTimeField(auto_now_add=True)
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"CheckIn for {self.subscription.name} - {self.response or 'pending'}"


class Nudge(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='nudges')
    scheduled_for = models.DateTimeField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Nudge for {self.subscription.name} at {self.scheduled_for}"