from rest_framework import serializers
from users.models import User

class PhoneAuthRequestSerializer(serializers.Serializer):
    """Запрос кода авторизации по номеру телефона"""
    phone = serializers.CharField()

class PhoneCodeVerifySerializer(serializers.Serializer):
    """Подтверждение кода авторизации"""
    phone = serializers.CharField()
    code = serializers.CharField()

class ActivateInviteCodeSerializer(serializers.Serializer):
    """Ввод чужого инвайт-кода"""
    invite_code = serializers.CharField()

class UserReferralProfileSerializer(serializers.ModelSerializer):
    """Профиль пользователя с информацией о рефералах"""
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'used_invite_code', 'invited_users']

    def get_invited_users(self, obj):
        return list(obj.invited_users.all().values_list('phone', flat=True))
