from django import template

register = template.Library()

@register.filter
def times(number):
    """
    Retourne une liste contenant number élements pour itérer
    """
    return range(number)

@register.filter
def dict_key(d, key):
    return d.get(key)

@register.filter
def stars(number):
    """
    Retourne un tuple (filled, empty) pour afficher les étoiles.
    filled = nombre d'étoiles remplies
    empty = nombre d'étoiles non remplies
    """
    filled = int(number)
    empty = 5 - filled
    return f"★" * filled + f"☆" * empty
