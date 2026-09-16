from rest_framework import generics, permissions, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from .models import Subscription, CheckIn
from .serializers import RegisterSerializer, UserSerializer, SubscriptionSerializer, CheckInSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        subscription = self.get_object()
        checkin = CheckIn.objects.create(subscription=subscription)
        serializer = CheckInSerializer(checkin)
        return Response(serializer.data, status=201)


class CheckInViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = CheckInSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CheckIn.objects.filter(subscription__user=self.request.user).order_by('-asked_at')

    def perform_update(self, serializer):
        checkin = serializer.save(responded_at=timezone.now())
        self._apply_flagging_logic(checkin)

    def _apply_flagging_logic(self, checkin):
        subscription = checkin.subscription
        if checkin.response == 'dont_use':
            subscription.status = 'flagged'
            subscription.save()
        elif checkin.response == 'still_use' and subscription.status == 'flagged':
            subscription.status = 'active'
            subscription.save()
        # 'not_sure' intentionally leaves status unchanged


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)

        active = subscriptions.filter(status='active')
        flagged = subscriptions.filter(status='flagged')

        total_monthly_burn = sum(s.monthly_cost for s in active)
        total_flagged_monthly = sum(s.monthly_cost for s in flagged)

        counts = subscriptions.values('status').annotate(count=Count('id'))
        status_counts = {row['status']: row['count'] for row in counts}

        upcoming_cutoff = timezone.now().date() + timedelta(days=30)
        upcoming_renewals = active.filter(
            next_renewal_date__lte=upcoming_cutoff
        ).order_by('next_renewal_date')

        category_breakdown = {}
        for sub in active:
            key = sub.category or 'uncategorized'
            category_breakdown[key] = category_breakdown.get(key, 0) + float(sub.monthly_cost)

        return Response({
            'total_monthly_burn': round(total_monthly_burn, 2),
            'total_flagged_monthly_waste': round(total_flagged_monthly, 2),
            'subscription_counts': {
                'active': status_counts.get('active', 0),
                'flagged': status_counts.get('flagged', 0),
                'cancelled': status_counts.get('cancelled', 0),
            },
            'category_breakdown': {k: round(v, 2) for k, v in category_breakdown.items()},
            'upcoming_renewals': SubscriptionSerializer(upcoming_renewals, many=True).data,
        })