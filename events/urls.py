from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RegistrationViewSet

# Router barcha endpointlarni avtomatik ulab chiqadi
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'registrations', RegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
]