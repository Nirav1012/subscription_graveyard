from django.contrib import admin
from .models import Subscription, CheckIn, Nudge

admin.site.register(Subscription)
admin.site.register(CheckIn)
admin.site.register(Nudge)