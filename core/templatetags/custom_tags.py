from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import mark_safe
import os
import re

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


@register.simple_tag
def static_versioned(path):
    """
    Return a static URL with a file modification timestamp query string.
    This helps browsers pick up rebuilt assets without manual cache clearing.
    """
    resolved_path = finders.find(path)
    if not resolved_path:
        return static(path)

    version = int(os.path.getmtime(resolved_path))
    return f"{static(path)}?v={version}"

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

@register.filter
def linebreaks_preserve_latex(value):
    """
    Convert newlines to <br> tags while preserving LaTeX math expressions.
    Protects both inline ($...$) and display ($$...$$) math from being mangled.
    Similar to Django's linebreaksbr but preserves LaTeX syntax.
    """
    if not value:
        return value
    
    value = str(value)
    
    # Protect display math ($$...$$) - must be done first
    display_math_blocks = []
    def save_display_math(match):
        display_math_blocks.append(match.group(0))
        placeholder = f"__DISPLAY_MATH_{len(display_math_blocks) - 1}__"
        return placeholder
    
    # Replace $$...$$ with placeholders
    value = re.sub(r'\$\$[\s\S]*?\$\$', save_display_math, value)
    
    # Protect inline math ($...$ but not $$)
    inline_math_blocks = []
    def save_inline_math(match):
        inline_math_blocks.append(match.group(0))
        placeholder = f"__INLINE_MATH_{len(inline_math_blocks) - 1}__"
        return placeholder
    
    # Match single $ ... $ (negative lookbehind/lookahead to avoid $$)
    value = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', save_inline_math, value, flags=re.DOTALL)
    
    # Convert newlines to <br> in remaining content
    value = value.replace('\n', '<br>')
    
    # Restore display math
    for i, block in enumerate(display_math_blocks):
        value = value.replace(f"__DISPLAY_MATH_{i}__", block)
    
    # Restore inline math
    for i, block in enumerate(inline_math_blocks):
        value = value.replace(f"__INLINE_MATH_{i}__", block)
    
    return mark_safe(value)
