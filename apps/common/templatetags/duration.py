from django import template

register = template.Library()


@register.filter
def format_duracion(minutos):
    """Convierte 90 → '1 h 30 min'. 60 → '1 h'. 45 → '45 min'."""
    try:
        m = int(minutos)
    except (TypeError, ValueError):
        return minutos
    if m < 60:
        return f'{m} min'
    h, r = divmod(m, 60)
    if r == 0:
        return f'{h} h'
    return f'{h} h {r} min'