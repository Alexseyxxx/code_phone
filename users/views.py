from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import random
import time
import logging
from users.models import User, AuthCode
from users.serializers import (
    PhoneAuthRequestSerializer,
    PhoneCodeVerifySerializer,
    UserReferralProfileSerializer,
    ActivateInviteCodeSerializer
)

logger = logging.getLogger(__name__)


class RequestCodeView(APIView):
    @swagger_auto_schema(
        request_body=PhoneAuthRequestSerializer,
        responses={200: openapi.Response('Код отправлен')}
    )
    def post(self, request):
        serializer = PhoneAuthRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = f"{random.randint(1000, 9999)}"
            AuthCode.objects.update_or_create(phone=phone, defaults={"code": code})
            logger.debug(f"Код авторизации для {phone}: {code}")
            time.sleep(2)
            return Response({"message": "Код отправлен"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    @swagger_auto_schema(
        request_body=PhoneCodeVerifySerializer,
        responses={200: "ОК", 400: "Неверный код", 404: "Код не найден"}
    )
    def post(self, request):
        serializer = PhoneCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        try:
            auth = AuthCode.objects.get(phone=phone)
        except AuthCode.DoesNotExist:
            return Response({"error": "Код не найден"}, status=404)

        if auth.code != code:
            return Response({"error": "Неверный код"}, status=400)

        user, created = User.objects.get_or_create(phone=phone)
        user.is_verified = True
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Авторизация прошла",
            "new_user": created,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserReferralProfileSerializer},
        security=[{'Bearer': []}],
    )
    def get(self, request):
        serializer = UserReferralProfileSerializer(request.user)
        return Response(serializer.data)


class ActivateInviteCodeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ActivateInviteCodeSerializer,
        responses={200: "Код активирован", 400: "Ошибка"},
        security=[{'Bearer': []}],
    )
    def post(self, request):
        serializer = ActivateInviteCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['invite_code']
        user = request.user

        if user.used_invite_code:
            return Response({'detail': 'Код уже был использован'}, status=400)

        try:
            inviter = User.objects.get(invite_code=code)
        except User.DoesNotExist:
            return Response({'detail': 'Неверный код'}, status=400)

        if inviter == user:
            return Response({'detail': 'Нельзя использовать свой код'}, status=400)

        user.used_invite_code = code
        inviter.invited_users.add(user)
        user.save()
        inviter.save()

        return Response({'detail': 'Код успешно активирован'})
