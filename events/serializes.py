from rest_framework import serializers
from .models import Event, Registration

class EventSerializer(serializers.ModelSerializer):
    # 4.4 Statistika: Ro'yxatdan o'tganlar va bo'sh joylar sonini chiqarib beramiz
    registered_count = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'event_type', 'location', 
                  'start_time', 'end_time', 'capacity', 'created_by', 
                  'registered_count', 'available_seats']
        read_only_fields = ['created_by']

    def get_registered_count(self, obj):
        return obj.registrations.filter(status='REGISTERED').count()

    def get_available_seats(self, obj):
        count = self.get_registered_count(obj)
        return max(0, obj.capacity - count)


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'user', 'event', 'status', 'created_at']
        read_only_fields = ['user', 'status']

    def validate(self, attrs):
        event = attrs['event']
        user = self.context['request'].user

        # Business Rule: capacity = 0 bo'lsa ro'yxatdan o'tish yopiladi
        if event.capacity == 0:
            raise serializers.ValidationError("Bu tadbirga ro'yxatdan o'tish yopilgan.")

        # Business Rule: Event capacity oshib ketmasligi kerak
        active_registrations = event.registrations.filter(status='REGISTERED').count()
        if active_registrations >= event.capacity:
            raise serializers.ValidationError("Kechirasiz, tadbirda bo'sh joy qolmagan.")

        return attrs