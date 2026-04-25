from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessGroup
from api.v1.permissions import IsAdmin
from api.v1.serializers.user import UserModelSerializer
from api.v1.serializers.access_group import (
    AccessGroupModelSerializer,
    AccessGroupCreateInputSerializer,
    AccessGroupCreateOutputSerializer,
    AccessGroupUpdateInputSerializer
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_group import AccessGroupService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_group import AccessGroupFilter


class AccessGroupViewSet(viewsets.GenericViewSet):
    """Управление группами доступа"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessGroupFilter

    def get_queryset(self):
        """Начальный список для работы"""
        user = self.request.user

        if user.is_staff:
            return AccessGroup.objects.all()
        else:
            user_groups = user.access_groups.filter(is_deleted=False)
            user_group_ids = user_groups.values_list('id', flat=True)

            registry_ids = AccessGroup.objects.filter(
                id__in=user_group_ids
            ).values_list('registry_id', flat=True).distinct()

            return AccessGroup.objects.filter(
                Q(id__in=user_group_ids) |
                Q(registry_id__in=registry_ids, owned_registries__isnull=False)
            ).filter(
                is_deleted=False
            ).distinct()

    def get_permissions(self):
        """Права на разные операции над группами"""

        if self.action in ['create', 'update', 'partial_update', 'destroy', 'restore']:
            return [IsAuthenticated(), IsAdmin()]
        else:
            return [IsAuthenticated()]

    @extend_schema(
        summary="Список групп доступа",
        description="Возвращает список всех доступных групп (с учетом прав)",
        responses={
            200: AccessGroupModelSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Группы доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(
                self.get_queryset()))
        output_serializer = AccessGroupModelSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Просмотр группы доступа",
        description="Возвращает информацию о конкретной группе доступа",
        responses={
            200: AccessGroupModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    def retrieve(self, request, pk=None):
        group = get_object_or_404(self.get_queryset(), id=pk)
        output_serializer = AccessGroupModelSerializer(group)
        return Response(output_serializer.data)

    @extend_schema(
        summary="Создание группы доступа",
        description="Создает новую группу доступа",
        request=AccessGroupCreateInputSerializer,
        responses={
            201: AccessGroupCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    def create(self, request):
        input_serializer = AccessGroupCreateInputSerializer(
            data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        group, error = AccessGroupService.create_group(
            input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка создания",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessGroupCreateOutputSerializer({
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'registry_id': group.registry_id,
            'parent_group_id': group.parent_group_id,
            'user_ids': list(group.users.values_list('id', flat=True)),
            'owner_of_registry_ids': list(group.owned_registries.values_list('id', flat=True))
        }).data

        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Частичное обновление группы доступа",
        description="Обновляет часть данных группы доступа",
        request=AccessGroupUpdateInputSerializer,
        responses={
            200: AccessGroupModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    def partial_update(self, request, pk=None):
        group = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, group)

        input_serializer = AccessGroupUpdateInputSerializer(
            data=request.data,
            partial=True
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_group, error = AccessGroupService.update_group(
            group, input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessGroupModelSerializer(updated_group).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное обновление группы доступа",
        description="Обновляет все данные группы доступа",
        request=AccessGroupUpdateInputSerializer,
        responses={
            200: AccessGroupModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    def update(self, request, pk=None):
        group = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, group)

        input_serializer = AccessGroupUpdateInputSerializer(
            data=request.data
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_group, error = AccessGroupService.update_group(
            group, input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessGroupModelSerializer(updated_group).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление группы доступа",
        description="Помечает группу доступа как удаленную",
        responses={
            204: OpenApiResponse(description="Успешное удаление"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    def destroy(self, request, pk=None):
        group = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, group)

        success, error = AccessGroupService.delete_group(group)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка удаления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Восстановление группы доступа",
        description="Восстанавливает удаленную группу доступа",
        responses={
            200: AccessGroupModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        group = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, group)

        success, error = AccessGroupService.restore_group(group)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessGroupModelSerializer(group).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Пользователи группы",
        description="Возвращает список пользователей в группе (с учётом наследования)",
        responses={
            200: UserModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    @action(detail=True, methods=['get'], url_path='users')
    def users(self, request, pk=None):
        """Получение списка пользователей в группе с учётом наследования"""
        group = get_object_or_404(self.get_queryset(), id=pk)
        users = group.get_all_users()

        if not request.user.is_staff:
            users = [u for u in users if not u.is_deleted]

        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserModelSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserModelSerializer(users, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Дерево групп",
        description="Возвращает дерево подгрупп для указанной группы",
        responses={
            200: AccessGroupModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Группы доступа']
    )
    @action(detail=True, methods=['get'], url_path='tree')
    def tree(self, request, pk=None):
        """Получение дерева подгрупп"""
        group = get_object_or_404(self.get_queryset(), id=pk)

        all_child_groups = group.get_all_children()

        groups_dict = {
            g.id: {
                'id': g.id,
                'name': g.name,
                'children': [],
                'parent_id': g.parent_group_id
            } for g in all_child_groups}
        groups_dict[group.id] = {
            'id': group.id,
            'name': group.name,
            'children': [],
            'parent_id': None
        }

        root = groups_dict[group.id]
        for g_id, g_data in groups_dict.items():
            parent_id = g_data['parent_id']
            if parent_id and parent_id in groups_dict:
                groups_dict[parent_id]['children'].append(g_data)

        def clean_tree(node):
            result = {'id': node['id'], 'name': node['name'], 'children': []}
            for child in node['children']:
                result['children'].append(clean_tree(child))
            return result

        return Response(clean_tree(root))
