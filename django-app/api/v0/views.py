from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


class StatusViewSet(viewsets.GenericViewSet):
    """Тестовый ViewSet для v0 (тестовая версия API)"""

    @action(detail=False, methods=['get'])
    def status(self, request):
        return Response({'status': 'ok'})
