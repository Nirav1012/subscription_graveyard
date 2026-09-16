from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command


def schedule_nudges():
    """For every active subscription with no pending nudge, schedule one 30 days out."""
    from .models import Subscription, Nudge
    for subscription in Subscription.objects.filter(status='active'):
        has_pending = Nudge.objects.filter(subscription=subscription, sent=False).exists()
        if not has_pending:
            Nudge.objects.create(
                subscription=subscription,
                scheduled_for=timezone.now() + timedelta(days=30),
            )


def send_due_nudges():
    """Turn any nudge whose time has come into an actual CheckIn prompt."""
    from .models import Nudge, CheckIn
    due_nudges = Nudge.objects.filter(sent=False, scheduled_for__lte=timezone.now())
    for nudge in due_nudges:
        CheckIn.objects.create(subscription=nudge.subscription)
        nudge.sent = True
        nudge.save()


def run_flag_stale_checkins():
    call_command('flag_stale_checkins')


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_nudges, 'interval', hours=24, id='schedule_nudges', replace_existing=True)
    scheduler.add_job(send_due_nudges, 'interval', minutes=5, id='send_due_nudges', replace_existing=True)
    scheduler.add_job(run_flag_stale_checkins, 'interval', hours=24, id='flag_stale_checkins', replace_existing=True)
    scheduler.start()

