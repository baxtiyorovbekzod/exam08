from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Event, Registration
from .serializes import EventSerializer, RegistrationSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def perform_create(self, serializer):
        
        serializer.save(created_by=self.request.user)

    
    @action(detail=False, methods=['get'])
    def top_events(self, request):
        events = Event.objects.annotate(
            active_regs=Count('registrations', filter=Q(registrations__status='REGISTERED'))
        ).order_by('-active_regs')[:5]
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        event_id = request.data.get('event')
        user = request.user

       
        existing_reg = Registration.objects.filter(user=user, event_id=event_id).first()
        if existing_reg:
            if existing_reg.status == 'REGISTERED':
                return Response({"detail": "Siz bu tadbirga allaqachon ro'yxatdan o'tgansiz."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                
                existing_reg.status = 'REGISTERED'
                existing_reg.save()
                serializer = self.get_serializer(existing_reg)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='REGISTERED')

    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        registration = self.get_object()
        
        if registration.status == 'CANCELLED':
            return Response({"detail": "Allaqachon bekor qilingan."}, status=status.HTTP_400_BAD_REQUEST)
        
        registration.status = 'CANCELLED'
        registration.save()
        return Response({"detail": "Ro'yxatdan o'tish muvaffaqiyatli bekor qilindi."}, status=status.HTTP_200_OK)