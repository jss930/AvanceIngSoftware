from django import template

register = template.Library()

@register.filter
def can_edit_reporte(reporte, user):
    """Filtro para verificar si un usuario puede editar un reporte"""
    return reporte.can_be_edited_by_user(user)