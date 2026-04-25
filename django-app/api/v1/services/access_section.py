from api.models import AccessSection, AccessRegistry


class AccessSectionService:
    """Сервис для работы с разделами доступа"""

    @staticmethod
    def create_section(data: dict) -> tuple:
        """Создание раздела доступа"""
        try:
            registry = AccessRegistry.objects.get(
                id=data['registry_id'],
                is_deleted=False
            )

            section = AccessSection.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                registry=registry
            )

            return section, None
        except Exception as e:
            return None, f"Ошибка создания раздела: {str(e)}"

    @staticmethod
    def update_section(section, data: dict) -> tuple:
        """Обновление раздела доступа"""
        try:
            if 'name' in data:
                section.name = data['name']
            if 'description' in data:
                section.description = data['description']

            section.save()
            return section, None
        except Exception as e:
            return None, f"Ошибка обновления раздела: {str(e)}"

    @staticmethod
    def delete_section(section) -> tuple:
        """Мягкое удаление раздела доступа"""
        if section.is_deleted:
            return False, "Раздел уже удален"

        if section.nodes.filter(is_deleted=False).exists():
            return False, "Невозможно удалить раздел, у которого есть узлы"

        section.is_deleted = True
        section.save()
        return True, None

    @staticmethod
    def restore_section(section) -> tuple:
        """Восстановление раздела доступа"""
        if not section.is_deleted:
            return False, "Раздел не был удален"

        if AccessSection.objects.filter(
            registry=section.registry,
            name=section.name,
            is_deleted=False
        ).exclude(id=section.id).exists():
            return False, "Раздел с таким именем уже существует в этом реестре"

        section.is_deleted = False
        section.save()
        return True, Non
