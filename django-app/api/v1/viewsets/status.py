from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.v1.serializers.status import StatusOutputSerializer


class StatusView(APIView):
    """Проверка статуса сервера"""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Проверка статуса сервера",
        description="Возвращает статус работы сервера.",
        responses={
            200: OpenApiResponse(
                response=StatusOutputSerializer,
                description="Корректная работа сервера"
            ),
            500: OpenApiResponse(
                description="Внутренняя ошибка сервера"
            )
        },
        tags=['Сервер']
    )
    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
