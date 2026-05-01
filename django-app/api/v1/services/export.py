import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from api.models import (
    AccessRegistry, AccessGroup, AccessSection,
    AccessNode, AccessObject, AccessType, AccessRight, User
)


class ExportService:
    @staticmethod
    def export_registry(registry: AccessRegistry, filters: dict) -> io.BytesIO:
        wb = Workbook()
        wb.remove(wb.active)

        groups_qs = AccessGroup.objects.filter(
            registry=registry, is_deleted=False)
        if filters.get('group_ids'):
            groups_qs = groups_qs.filter(id__in=filters['group_ids'])
        groups = list(groups_qs.order_by('name'))
        ws_users = wb.create_sheet("Пользователи")
        ExportService._build_users_sheet(ws_users, groups)

        sections_qs = AccessSection.objects.filter(
            registry=registry, is_deleted=False)
        if filters.get('section_ids'):
            sections_qs = sections_qs.filter(id__in=filters['section_ids'])
        sections = list(sections_qs.order_by('name'))

        for section in sections:
            sheet_title = section.name[:31]
            ws = wb.create_sheet(title=sheet_title)
            ExportService._build_section_sheet(ws, section, groups, filters)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def _apply_header_style(ws, num_columns):
        """Применяет стили к строке заголовков."""
        header_fill = PatternFill(
            start_color="B7DEE8", end_color="B7DEE8", fill_type="solid")
        header_font = Font(bold=True)
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        for col_idx in range(1, num_columns + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border

    @staticmethod
    def _build_users_sheet(ws, groups):
        """Заполняет лист «Пользователи»: столбцы 'Группа', 'ФИО', 'Должность'."""
        headers = ['Группа', 'ФИО', 'Должность']
        ws.append(headers)

        ExportService._apply_header_style(ws, len(headers))
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        row = 2
        for group in groups:
            users = User.objects.filter(
                access_groups=group,
                is_deleted=False
            ).order_by('last_name', 'first_name')

            if not users:
                ws.cell(row=row, column=1, value=group.name)
                row += 1
                continue

            for user in users:
                ws.cell(row=row, column=1, value=group.name)
                initials = f"{user.first_name[0]}."
                if user.patronymic:
                    initials += f"{user.patronymic[0]}."
                full_name = f"{user.last_name} {initials}"
                ws.cell(row=row, column=2, value=full_name)
                ws.cell(row=row, column=3, value=user.post)
                row += 1

        for r in range(2, row):
            for c in range(1, 4):
                cell = ws.cell(row=r, column=c)
                cell.border = thin_border
                cell.alignment = Alignment(vertical='center')

        for col_idx in range(1, 4):
            max_length = 0
            col_letter = get_column_letter(col_idx)
            for r in range(1, row):
                val = ws.cell(row=r, column=col_idx).value
                if val:
                    max_length = max(max_length, len(str(val)))
            ws.column_dimensions[col_letter].width = min(max_length + 2, 40)

    @staticmethod
    def _build_section_sheet(ws, section, groups, filters):
        rows_data = []
        nodes_qs = AccessNode.objects.filter(section=section, is_deleted=False)
        if filters.get('node_ids'):
            nodes_qs = nodes_qs.filter(id__in=filters['node_ids'])
        nodes = nodes_qs.order_by('name')

        for node in nodes:
            objects_qs = AccessObject.objects.filter(
                node=node, is_deleted=False)
            if filters.get('object_ids'):
                objects_qs = objects_qs.filter(id__in=filters['object_ids'])
            objects = objects_qs.order_by('name')
            for obj in objects:
                types_qs = AccessType.objects.filter(
                    object=obj, is_deleted=False).select_related('template')
                types = types_qs.order_by('template__name')
                for at in types:
                    assigned_group_ids = set(
                        AccessRight.objects.filter(access_type=at)
                        .values_list('group_id', flat=True)
                    )
                    rights = {group.id: (group.id in assigned_group_ids)
                              for group in groups}
                    rows_data.append((
                        node.name,
                        node.ip or '',
                        obj.resource_path,
                        obj.description or '',
                        at.template.name,
                        node.id,
                        obj.id,
                        rights
                    ))

        headers = ['Доменное имя', 'IP-адрес', 'Путь к ресурсу', 'Описание', 'Тип доступа'] + \
                  [group.name for group in groups]
        ws.append(headers)
        ExportService._apply_header_style(ws, len(headers))

        if not rows_data:
            return

        current_row = 2
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        center_align = Alignment(horizontal='center', vertical='center')
        left_align = Alignment(vertical='center', wrap_text=True)

        node_start_row = current_row
        obj_start_row = current_row
        last_node_id = None
        last_obj_id = None

        for idx, row_data in enumerate(rows_data):
            (node_name, node_ip, obj_path, obj_desc,
             type_name, node_id, obj_id, rights) = row_data

            ws.cell(row=current_row, column=1, value=node_name)
            ws.cell(row=current_row, column=2, value=node_ip)
            ws.cell(row=current_row, column=3, value=obj_path)
            ws.cell(row=current_row, column=4, value=obj_desc)
            ws.cell(row=current_row, column=5, value=type_name)

            for i, group in enumerate(groups):
                sign = '+' if rights.get(group.id) else ''
                ws.cell(row=current_row, column=6 + i, value=sign)

            if idx == 0:
                last_node_id = node_id
                last_obj_id = obj_id
                current_row += 1
                continue

            if node_id != last_node_id:
                if node_start_row < current_row - 1:
                    ws.merge_cells(start_row=node_start_row, start_column=1,
                                   end_row=current_row - 1, end_column=1)
                    ws.merge_cells(start_row=node_start_row, start_column=2,
                                   end_row=current_row - 1, end_column=2)
                if obj_start_row < current_row - 1:
                    ws.merge_cells(start_row=obj_start_row, start_column=3,
                                   end_row=current_row - 1, end_column=3)
                    ws.merge_cells(start_row=obj_start_row, start_column=4,
                                   end_row=current_row - 1, end_column=4)

                node_start_row = current_row
                obj_start_row = current_row
                last_node_id = node_id
                last_obj_id = obj_id
            else:
                if obj_id != last_obj_id:
                    if obj_start_row < current_row - 1:
                        ws.merge_cells(start_row=obj_start_row, start_column=3,
                                       end_row=current_row - 1, end_column=3)
                        ws.merge_cells(start_row=obj_start_row, start_column=4,
                                       end_row=current_row - 1, end_column=4)
                    obj_start_row = current_row
                    last_obj_id = obj_id

            current_row += 1

        end_row = current_row - 1
        if node_start_row < end_row:
            ws.merge_cells(start_row=node_start_row, start_column=1,
                           end_row=end_row, end_column=1)
            ws.merge_cells(start_row=node_start_row, start_column=2,
                           end_row=end_row, end_column=2)
        if obj_start_row < end_row:
            ws.merge_cells(start_row=obj_start_row, start_column=3,
                           end_row=end_row, end_column=3)
            ws.merge_cells(start_row=obj_start_row, start_column=4,
                           end_row=end_row, end_column=4)

        for r in range(2, current_row):
            for c in range(1, len(headers) + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = thin_border
                cell.alignment = center_align if c >= 6 else left_align

        for col_idx in range(1, len(headers) + 1):
            max_length = 0
            col_letter = get_column_letter(col_idx)
            for r in range(1, current_row):
                val = ws.cell(row=r, column=col_idx).value
                if val:
                    max_length = max(max_length, len(str(val)))
            ws.column_dimensions[col_letter].width = min(max_length + 2, 40)
