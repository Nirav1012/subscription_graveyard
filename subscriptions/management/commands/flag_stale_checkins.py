from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from subscriptions.models import CheckIn


class Command(BaseCommand):
    help = "Flags subscriptions whose check-in prompts have gone unanswered for 60+ days"

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=60)
        stale_checkins = CheckIn.objects.filter(
            response__isnull=True,
            asked_at__lt=cutoff,
            subscription__status='active',
        )
        count = 0
        for checkin in stale_checkins:
            checkin.subscription.status = 'flagged'
            checkin.subscription.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Flagged {count} subscription(s) due to unanswered check-ins."))